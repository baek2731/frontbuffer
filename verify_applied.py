#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_applied.py - 수정본이 실제로 적용되었는지 3단계로 확인합니다 (읽기 전용).

저장소 루트에서 실행합니다.

    python verify_applied.py                     기록부의 verified 글 전체 확인
    python verify_applied.py --since 2026-10-16  last_modified_at(또는 date)이 그 날짜 이후인 글만
    python verify_applied.py --batch Chrome1     기록부 batch 이름에 포함된 글만
    python verify_applied.py --no-live           사이트 접속 없이 로컬·Git 만 확인
    python verify_applied.py --csv result.csv    결과를 CSV 로 저장
    python verify_applied.py --fill-baseline     기준 단어 수가 없는 글에 현재 상태를 기준으로 기록

확인 단계
  1. 로컬  : 글의 본문 단어 수가 기록부(research_data/revision_log.csv)의 body_words 와 같은가
  2. Git   : 커밋 안 했거나 푸시 안 한 변경이 없는가
  3. 라이브: 실제 사이트 주소의 내용에 로컬 본문의 문장(처음부터 끝까지 고르게 최대 12개)이 모두 들어 있는가
라이브 확인은 푸시 후 Pages 배포(몇 분)가 끝나야 맞게 나옵니다.
Python 3.10 호환, 표준 라이브러리만 사용합니다.
"""
import argparse
import csv
import glob
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LEDGER_PATH = os.path.join("research_data", "revision_log.csv")
DEFAULT_BASE_URL = "https://frontbuffer.net"
WORDS_TOLERANCE = 3
PROBE_CHARS = 50       # 문장 확인에 쓰는 글자 수(영문·숫자·한글만 남긴 뒤)
MIN_LINE = 60          # 확인용 줄의 최소 길이
MAX_PROBES = 12        # 글 하나당 확인용 문장 최대 개수


# ---------------------------------------------------------------- 공통
def git(args):
    try:
        p = subprocess.run(["git", "-c", "core.quotepath=off"] + args,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.returncode, p.stdout.decode("utf-8", errors="replace")
    except OSError:
        return 1, ""


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        q = v[0]
        v = v[1:-1]
        v = v.replace("''", "'") if q == "'" else v.replace('\\"', '"')
    return v


def parse_front_matter(text):
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}, text
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    if len(parts) < 3:
        return {}, text
    fm = {}
    lines = parts[1].splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        j = i + 1
        block = []
        while j < len(lines) and (lines[j].startswith((" ", "\t")) or lines[j].strip().startswith("- ")):
            block.append(lines[j].strip())
            j += 1
        if val in (">", ">-", "|", "|-") and block:
            val = " ".join(block)
        elif val == "" and block:
            val = "[" + ", ".join(b[2:].strip() if b.startswith("- ") else b for b in block) + "]"
        fm[key] = val
        i = j if block else i + 1
    return fm, parts[2]


def split_sources(body):
    """본문과 Sources 블록을 나눕니다."""
    lines = body.splitlines()
    for idx, ln in enumerate(lines):
        if re.match(r"^(#{1,6}\s*)?\*?_?sources?\*?_?\s*:?\s*\*?$", ln.strip(), flags=re.I):
            return "\n".join(lines[:idx])
    return body


def clean_word_count(body):
    lines = []
    in_code = False
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.match(r"^(#{1,6}\s*)?\*?_?sources?\*?_?\s*:?\s*\*?$", s, flags=re.I):
            break
        lines.append(ln)
    t = "\n".join(lines)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"[|`*_#>\-]+", " ", t)
    return len(t.split())


def normalize(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def md_plain(p):
    p = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", p)
    p = re.sub(r"[*_`]+", "", p)
    return p.strip()


def pick_probes(body):
    """본문의 줄(문단, 목록, 표 행)에서 앞부분을 골라 확인용 문장으로 씁니다.
    후보가 많으면 처음부터 끝까지 고르게 최대 MAX_PROBES 개를 씁니다."""
    main = split_sources(body)
    cand = []
    for ln in main.splitlines():
        s = ln.strip()
        if not s or s.startswith(("#", "![", "<", ">")) or "{%" in s:
            continue
        if re.fullmatch(r"[|\-:\s]+", s) or s == "---":
            continue
        s = re.sub(r"^([-*+]|\d+\.)\s+", "", s)
        plain = md_plain(s.replace("|", " "))
        plain = re.sub(r"\s+", " ", plain)
        if len(plain) >= MIN_LINE:
            cand.append(plain)
    if not cand:
        return []
    if len(cand) > MAX_PROBES:
        step = (len(cand) - 1) / float(MAX_PROBES - 1)
        cand = [cand[int(round(i * step))] for i in range(MAX_PROBES)]
    probes = []
    for p in cand:
        n = normalize(p)[:PROBE_CHARS]
        if len(n) >= 20 and n not in probes:
            probes.append(n)
    return probes


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip > 0:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_text(html):
    p = TextExtractor()
    try:
        p.feed(html)
    except Exception:
        pass
    return " ".join(p.parts)


def read_base_url():
    if os.path.exists("_config.yml"):
        with open("_config.yml", "rb") as f:
            t = f.read().decode("utf-8", errors="ignore")
        m = re.search(r"^url\s*:\s*[\"']?([^\"'\s]+)", t, flags=re.M)
        if m:
            return m.group(1).rstrip("/")
    return DEFAULT_BASE_URL


def jekyll_slug(fname):
    """Jekyll 의 :title 슬러그: 대소문자는 그대로 두고, 허용 문자 외에는 '-', 앞뒤 '-' 제거."""
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", fname)
    if slug.endswith(".md"):
        slug = slug[:-3]
    slug = re.sub(r"[^\w.~!$&'()+,;=@]+", "-", slug)
    return slug.strip("-")


def post_url(base, fname, fm):
    perm = unquote(fm.get("permalink", ""))
    if perm:
        return base + (perm if perm.startswith("/") else "/" + perm)
    cats = [unquote(c) for c in fm.get("categories", "").strip().strip("[]").split(",") if c.strip()]
    if not cats:
        return ""
    return "%s/%s/%s/" % (base, "/".join(cats), jekyll_slug(fname))


def read_ledger():
    led = {}
    if not os.path.exists(LEDGER_PATH):
        return led
    with open(LEDGER_PATH, "rb") as f:
        text = f.read().decode("utf-8-sig", errors="ignore")
    for row in csv.DictReader(text.splitlines()):
        name = (row.get("file") or "").strip()
        if name:
            led[name] = row
    return led


def fetch(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (verify_applied; read-only check)"})
    last = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                return r.status, data.decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            return e.code, ""
        except Exception as e:  # 네트워크 오류 등
            last = e
            time.sleep(1)
    return 0, str(last)


def fill_baseline():
    """body_words 가 비어 있는 verified 글에 현재 로컬 본문 단어 수를 기록합니다 (기록부 CSV 만 수정)."""
    with open(LEDGER_PATH, "rb") as f:
        text = f.read().decode("utf-8-sig", errors="ignore")
    rows = list(csv.DictReader(text.splitlines()))
    cols = ["file", "status", "batch", "verified_at", "notes", "body_words"]
    n = 0
    for r in rows:
        if (r.get("status") or "").strip() != "verified" or (r.get("body_words") or "").strip():
            continue
        path = os.path.join("_posts", r["file"])
        if not os.path.exists(path):
            continue
        with open(path, "rb") as fh:
            fm, body = parse_front_matter(fh.read().decode("utf-8", errors="ignore"))
        r["body_words"] = str(clean_word_count(body))
        n += 1
    with open(LEDGER_PATH, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("기준 단어 수를 기록한 글: %d편 (%s)" % (n, LEDGER_PATH))


# ---------------------------------------------------------------- 본체
def main():
    ap = argparse.ArgumentParser(description="수정본 적용 여부 확인 (읽기 전용)")
    ap.add_argument("--since", default="", help="이 날짜(YYYY-MM-DD) 이후 수정·작성한 글만")
    ap.add_argument("--batch", default="", help="기록부 batch 이름에 포함된 글만")
    ap.add_argument("--no-live", action="store_true", help="사이트 접속 없이 로컬·Git 만 확인")
    ap.add_argument("--base-url", default="", help="사이트 주소를 직접 지정(시험용)")
    ap.add_argument("--sleep", type=float, default=0.4, help="요청 사이 대기(초)")
    ap.add_argument("--timeout", type=float, default=20, help="요청 제한 시간(초)")
    ap.add_argument("--csv", default="", help="결과를 저장할 CSV 경로")
    ap.add_argument("--fill-baseline", action="store_true",
                    help="기록부에서 body_words 가 빈 verified 글에 현재 로컬 본문 단어 수를 기록 (기록부만 수정)")
    args = ap.parse_args()

    if not os.path.isdir("_posts"):
        print("_posts 폴더가 없습니다. 저장소 루트에서 실행하세요.")
        sys.exit(1)

    ledger = read_ledger()
    if not ledger:
        print("기록부(%s)가 없거나 비어 있습니다." % LEDGER_PATH)
        sys.exit(1)

    if args.fill_baseline:
        fill_baseline()
        return

    base = args.base_url.rstrip("/") if args.base_url else read_base_url()

    code, out = git(["status", "--porcelain", "--", "_posts"])
    status = {}
    for line in out.splitlines():
        if len(line) > 3:
            path = line[3:].strip().strip('"')
            if " -> " in path:
                path = path.split(" -> ")[-1].strip().strip('"')
            status[path.replace("\\", "/")] = line[:2].strip()
    c, up = git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    upstream = up.strip() if c == 0 else ""
    unpushed = set()
    if upstream:
        c2, o2 = git(["diff", "--name-only", upstream + "..HEAD", "--", "_posts"])
        unpushed = set(x.strip().replace("\\", "/") for x in o2.splitlines() if x.strip())

    targets = []
    for name, row in sorted(ledger.items()):
        if (row.get("status") or "").strip() != "verified":
            continue
        if args.batch and args.batch not in (row.get("batch") or ""):
            continue
        targets.append((name, row))

    results = []
    missing_files = []
    for name, row in targets:
        path = os.path.join("_posts", name)
        if not os.path.exists(path):
            missing_files.append(name)
            continue
        with open(path, "rb") as fh:
            text = fh.read().decode("utf-8", errors="ignore")
        fm, body = parse_front_matter(text)
        if args.since:
            d = fm.get("date", "")[:10]
            lm = fm.get("last_modified_at", "")[:10]
            if not ((d and d >= args.since) or (lm and lm >= args.since)):
                continue
        words = clean_word_count(body)
        bw = (row.get("body_words") or "").strip()
        if bw.isdigit():
            local = "OK" if abs(int(bw) - words) <= WORDS_TOLERANCE else "다름(%s→%d)" % (bw, words)
        else:
            local = "기준없음"
        norm = path.replace("\\", "/")
        g = status.get(norm, "")
        git_state = "OK"
        if g:
            git_state = "미커밋(%s)" % g
        elif norm in unpushed:
            git_state = "미푸시"
        results.append({
            "file": name, "local": local, "git": git_state, "live": "-",
            "url": post_url(base, name, fm), "probes": pick_probes(body),
        })

    if not args.no_live:
        for r in results:
            if not r["url"]:
                r["live"] = "주소불명"
                continue
            st, html = fetch(r["url"], args.timeout)
            if st == 200:
                live_norm = normalize(html_text(html))
                probes = r["probes"]
                if not probes:
                    r["live"] = "확인문장없음"
                else:
                    miss = [p for p in probes if p not in live_norm]
                    r["live"] = "OK" if not miss else "내용다름(%d/%d)" % (len(probes) - len(miss), len(probes))
            elif st == 0:
                r["live"] = "접속실패"
            else:
                r["live"] = "HTTP %d" % st
            time.sleep(args.sleep)

    def verdict(r):
        bad = []
        if r["local"] not in ("OK", "기준없음"):
            bad.append("로컬")
        if r["git"] != "OK":
            bad.append("Git")
        if not args.no_live and r["live"] not in ("OK", "-"):
            bad.append("라이브")
        return bad

    print("=" * 74)
    print("적용 확인 (%s)  기준 주소: %s" % (time.strftime("%Y-%m-%d %H:%M"), base))
    print("=" * 74)
    print("%-52s %-10s %-10s %s" % ("파일", "로컬", "Git", "라이브"))
    print("-" * 74)
    problems = []
    for r in results:
        b = verdict(r)
        mark = "  " if not b else "!!"
        print("%s %-50s %-10s %-10s %s" % (mark, r["file"][:50], r["local"], r["git"], r["live"]))
        if b:
            problems.append((r, b))

    print("")
    if not results:
        print("조건에 맞는 글이 없습니다. (--since, --batch 조건을 확인하세요)")
        return
    print("확인한 글: %d편  /  문제 있음: %d편" % (len(results), len(problems)))
    if missing_files:
        print("")
        print("[기록부에는 있는데 폴더에 없는 파일 %d개]" % len(missing_files))
        for m in missing_files:
            print("  - %s" % m)
    if problems:
        print("")
        print("[문제 해석]")
        print("  로컬 '다름'    : 내가 전달한 최종본이 아니거나, 이후에 수정한 글입니다. 파일을 다시 덮어쓰세요.")
        print("  Git '미커밋'   : 파일을 고쳤지만 git add/commit 을 하지 않았습니다.")
        print("  Git '미푸시'   : 커밋은 했지만 git push 를 하지 않았습니다.")
        print("  라이브 'HTTP 404': 사이트에 아직 없습니다. 푸시 직후라면 배포(몇 분)를 기다리세요.")
        print("  라이브 '내용다름': 사이트의 내용이 로컬과 다릅니다. 배포 대기이거나 푸시가 안 된 것입니다.")
        print("  라이브 '접속실패': 네트워크 문제입니다. 잠시 뒤 다시 실행하세요.")
    else:
        print("")
        print("모든 글이 로컬, Git, 라이브에서 일치합니다.")

    if args.csv:
        with open(args.csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["file", "local", "git", "live", "url"])
            for r in results:
                w.writerow([r["file"], r["local"], r["git"], r["live"], r["url"]])
        print("")
        print("%s 저장" % args.csv)


if __name__ == "__main__":
    main()
