#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""post_status.py v2 - 로컬 _posts 와 Git 상태를 집계합니다 (읽기 전용, 파일을 바꾸지 않음).

저장소 루트에서 실행합니다.

    python post_status.py                        기본 점검 (글 수, 기록부 대조, Git 상태, front matter)
    python post_status.py --og                   마지막 OG 재생성 이후 제목·요약이 바뀐 글의 날짜
    python post_status.py --og --include-uncommitted   커밋 전 수정까지 포함
    python post_status.py --urls                 색인 요청용 순수 URL 목록 (전체)
    python post_status.py --urls --since 2026-10-10    그 날짜 이후 작성·수정한 글만
    python post_status.py --no-csv               post_status.csv 를 만들지 않음

기록부(ledger): research_data/revision_log.csv  (열: file,status,batch,verified_at,notes,body_words)
  body_words 는 전달·검증한 시점의 본문 단어 수입니다. 로컬 글과 3단어 넘게 다르면 '전달본과 다름'으로 표시합니다.
  status 는 verified 또는 unverified. 기록부에 없는 글은 '신규(미등록)'로 표시됩니다.
  새 글을 검증했으면 이 파일에 한 줄 추가하세요.

규칙값은 아래 상수에서 바꿉니다. Python 3.10 호환.
"""
import argparse
import csv
import glob
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ---- 규칙값 (필요하면 여기만 고치세요) ----
TITLE_MAX = 65
EXCERPT_MIN = 140
EXCERPT_MAX = 160
LEDGER_PATH = os.path.join("research_data", "revision_log.csv")
OG_COMMIT_PATTERN = "OG 이미지 재생성"
DEFAULT_BASE_URL = "https://frontbuffer.net"
WORDS_TOLERANCE = 3  # 기록부 body_words 와 로컬 본문 단어 수의 허용 오차
# -------------------------------------------


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
        if q == "'":
            v = v.replace("''", "'")
        else:
            v = v.replace('\\"', '"')
    return v


def parse_front_matter(text):
    """front matter 를 (dict, 본문) 으로 나눕니다. 여러 줄 값(>-, |, 목록)을 단순 지원합니다."""
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}, text
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    if len(parts) < 3:
        return {}, text
    fm_lines = parts[1].splitlines()
    body = parts[2]
    fm = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        j = i + 1
        block = []
        while j < len(fm_lines) and (fm_lines[j].startswith((" ", "\t")) or fm_lines[j].strip().startswith("- ")):
            block.append(fm_lines[j].strip())
            j += 1
        if val in (">", ">-", "|", "|-") and block:
            val = " ".join(block)
        elif val == "" and block:
            val = "[" + ", ".join(b[2:].strip() if b.startswith("- ") else b for b in block) + "]"
        fm[key] = val
        i = j if block else i + 1
    return fm, body


def clean_word_count(body):
    """본문 단어 수. Sources 블록, 코드 블록, URL 은 제외합니다."""
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


def categories_of(fm):
    raw = fm.get("categories", "")
    raw = raw.strip().strip("[]")
    return [unquote(c) for c in raw.split(",") if c.strip()]


def post_url(base, fname, fm):
    perm = unquote(fm.get("permalink", ""))
    if perm:
        return base + (perm if perm.startswith("/") else "/" + perm)
    cats = categories_of(fm)
    if not cats:
        return ""
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", fname)[:-3]
    return "%s/%s/%s/" % (base, "/".join(cats), slug)  # Jekyll :categories 는 여러 개면 / 로 이어 붙임


def read_base_url():
    if os.path.exists("_config.yml"):
        with open("_config.yml", "rb") as f:
            t = f.read().decode("utf-8", errors="ignore")
        m = re.search(r"^url\s*:\s*[\"']?([^\"'\s]+)", t, flags=re.M)
        if m:
            return m.group(1).rstrip("/")
    return DEFAULT_BASE_URL


def read_ledger():
    led = {}
    if not os.path.exists(LEDGER_PATH):
        return led, False
    with open(LEDGER_PATH, "rb") as f:
        text = f.read().decode("utf-8-sig", errors="ignore")
    for row in csv.DictReader(text.splitlines()):
        name = (row.get("file") or "").strip()
        if name:
            led[name] = row
    return led, True


def load_posts():
    posts = []
    for f in sorted(glob.glob(os.path.join("_posts", "*.md"))):
        with open(f, "rb") as fh:
            text = fh.read().decode("utf-8", errors="ignore")
        fm, body = parse_front_matter(text)
        posts.append({
            "path": f.replace("\\", "/"),
            "file": os.path.basename(f),
            "fm": fm,
            "title": unquote(fm.get("title", "")),
            "excerpt": unquote(fm.get("excerpt", "")),
            "date": fm.get("date", ""),
            "lm": fm.get("last_modified_at", ""),
            "words": clean_word_count(body),
        })
    return posts


def git_state():
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
    return status, upstream, unpushed


def cmd_urls(posts, since):
    base = read_base_url()
    n = 0
    for p in posts:
        if since:
            d = p["date"][:10]
            lm = p["lm"][:10]
            if not ((d and d >= since) or (lm and lm >= since)):
                continue
        u = post_url(base, p["file"], p["fm"])
        if u:
            print(u)
            n += 1
        else:
            sys.stderr.write("[건너뜀] categories 없음: %s\n" % p["file"])
    sys.stderr.write("URL %d개\n" % n)


def cmd_og(include_uncommitted):
    c, h = git(["log", "--grep=" + OG_COMMIT_PATTERN, "-n", "1", "--format=%H %s"])
    h = h.strip()
    if c != 0 or not h:
        print("'%s' 커밋을 찾지 못했습니다. git log 로 OG 재생성 커밋 메시지를 확인하세요." % OG_COMMIT_PATTERN)
        return
    commit, subject = h.split(" ", 1)
    print("기준 커밋: %s  %s" % (commit[:8], subject))
    target = [] if include_uncommitted else ["HEAD"]
    c1, names = git(["diff", "--name-status", commit] + target + ["--", "_posts"])
    added = set()
    for ln in names.splitlines():
        parts = ln.split("\t")
        if parts and parts[0].startswith("A") and len(parts) > 1:
            added.add(parts[-1].replace("\\", "/"))
    c2, diff = git(["diff", commit] + target + ["-U0", "--no-color", "--", "_posts"])
    cur = ""
    changed = {}
    for ln in diff.splitlines():
        if ln.startswith("+++ b/"):
            cur = ln[6:].replace("\\", "/")
            continue
        if ln.startswith("+") and not ln.startswith("+++"):
            if ln.startswith("+title:") or ln.startswith("+excerpt:"):
                changed.setdefault(cur, set()).add(ln[1:].split(":", 1)[0])
    dates = []
    print("")
    for path, fields in sorted(changed.items()):
        base = os.path.basename(path)
        m = re.match(r"^(\d{4}-\d{2}-\d{2})", base)
        if path in added:
            print("  (새 글, 발행 시 OG 자동 생성) %s" % base)
            continue
        if m:
            dates.append(m.group(1))
            print("  %s  [%s]" % (base, ", ".join(sorted(fields))))
    print("")
    if dates:
        print("OG 재생성 날짜 입력값:")
        print(" ".join(sorted(set(dates))))
    else:
        print("제목·요약이 바뀐 기존 글이 없습니다. OG 재생성이 필요 없습니다.")


def cmd_report(posts, no_csv):
    ledger, has_ledger = read_ledger()
    status, upstream, unpushed = git_state()

    names = set(p["file"] for p in posts)
    rows = []
    issues = []
    diffs = []
    for p in posts:
        f = p["file"]
        led = ledger.get(f)
        if led is None:
            state = "신규(미등록)"
        else:
            state = (led.get("status") or "").strip() or "unverified"
        d = p["date"]
        if not re.match(r"^\d{4}-\d{2}-\d{2}", d):
            issues.append("date 형식 이상: %s (%s)" % (f, d))
        else:
            fd = re.match(r"^(\d{4}-\d{2}-\d{2})", f)
            if fd and fd.group(1) != d[:10]:
                issues.append("파일명 날짜와 date 불일치: %s (date: %s)" % (f, d[:10]))
        if len(p["title"]) > TITLE_MAX:
            issues.append("제목 %d자(%d 초과): %s" % (len(p["title"]), TITLE_MAX, f))
        if not p["excerpt"]:
            issues.append("요약 없음: %s" % f)
        elif not (EXCERPT_MIN <= len(p["excerpt"]) <= EXCERPT_MAX):
            issues.append("요약 %d자(%d~%d 밖): %s" % (len(p["excerpt"]), EXCERPT_MIN, EXCERPT_MAX, f))
        delivered = (led or {}).get("body_words", "").strip()
        mismatch = ""
        if delivered.isdigit() and abs(int(delivered) - p["words"]) > WORDS_TOLERANCE:
            mismatch = "Y"
            diffs.append((f, int(delivered), p["words"]))
        rows.append({
            "file": f, "title": p["title"], "date": d, "last_modified_at": p["lm"],
            "words_body": p["words"], "ledger": state, "delivered_words": delivered, "mismatch": mismatch,
            "batch": (led or {}).get("batch", ""),
            "git": status.get(p["path"], ""),
            "unpushed": "Y" if p["path"] in unpushed else "",
        })

    verified = [r for r in rows if r["ledger"] == "verified"]
    unverified = [r for r in rows if r["ledger"] == "unverified"]
    new = [r for r in rows if r["ledger"] == "신규(미등록)"]
    missing = sorted(set(ledger.keys()) - names)
    modified = [r for r in rows if r["git"] in ("M", "R")]
    untracked = [r for r in rows if r["git"] == "??"]
    unpushed_rows = [r for r in rows if r["unpushed"]]

    print("=" * 60)
    print("로컬 _posts 집계 (이 PC의 파일을 직접 읽은 결과)")
    print("=" * 60)
    print("글 파일 수                   : %d" % len(rows))
    if has_ledger:
        print("기록부: verified            : %d" % len(verified))
        print("기록부: unverified          : %d" % len(unverified))
        print("기록부에 없음(신규)         : %d" % len(new))
    else:
        print("기록부(%s)가 없습니다. 수정 상태는 last_modified_at 유무로만 참고하세요." % LEDGER_PATH)
        print("last_modified_at 있음       : %d" % len([r for r in rows if r["last_modified_at"]]))
    print("")
    if has_ledger and new:
        print("[기록부에 없는 글: 새 글이거나 아직 등록 안 한 글]")
        for r in new:
            print("  - %s%s" % (r["file"], "  (last_modified_at 표시는 있음)" if r["last_modified_at"] else ""))
        print("")
    if missing:
        print("[기록부에는 있는데 폴더에 없는 파일: 삭제 또는 이름 변경]")
        for m in missing:
            print("  - %s" % m)
        print("")
    if diffs:
        print("[전달본과 본문이 다른 글: 전달본이 반영되지 않았거나 이후에 수정됨]")
        for f, a, b in diffs:
            print("  - %s  (전달본 %d단어 / 로컬 %d단어)" % (f, a, b))
        print("")
    print("Git 상태")
    print("  기준 브랜치               : %s" % (upstream or "(원격 추적 브랜치 없음)"))
    print("  수정했지만 커밋 안 함     : %d" % len(modified))
    print("  새 파일(추적 안 됨)       : %d" % len(untracked))
    print("  커밋했지만 푸시 안 함     : %d" % len(unpushed_rows))
    for title, lst in (("수정했지만 커밋 안 한 글", modified), ("새 파일", untracked), ("푸시 안 한 글", unpushed_rows)):
        if lst:
            print("")
            print("[%s]" % title)
            for r in lst:
                print("  - %s" % r["file"])
    print("")
    print("front matter 점검 (%d건)" % len(issues))
    for i in issues[:40]:
        print("  - %s" % i)
    if len(issues) > 40:
        print("  ... 외 %d건" % (len(issues) - 40))

    if not no_csv:
        with open("post_status.csv", "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["file", "title", "date", "last_modified_at", "words_body", "delivered_words", "mismatch", "ledger", "batch", "git", "unpushed"])
            for r in rows:
                w.writerow([r["file"], r["title"], r["date"], r["last_modified_at"], r["words_body"],
                            r["delivered_words"], r["mismatch"], r["ledger"], r["batch"], r["git"], r["unpushed"]])
        print("")
        print("post_status.csv 저장 (.gitignore 에 추가해 저장소에 올리지 않게 하세요)")


def main():
    ap = argparse.ArgumentParser(description="로컬 _posts 와 Git 상태 점검 (읽기 전용)")
    ap.add_argument("--og", action="store_true", help="마지막 OG 재생성 이후 제목·요약이 바뀐 글의 날짜")
    ap.add_argument("--include-uncommitted", action="store_true", help="--og 에서 커밋 전 수정도 포함")
    ap.add_argument("--urls", action="store_true", help="색인 요청용 URL 목록")
    ap.add_argument("--since", default="", help="--urls 에서 이 날짜(YYYY-MM-DD) 이후 글만")
    ap.add_argument("--no-csv", action="store_true", help="CSV 를 만들지 않음")
    args = ap.parse_args()

    if not os.path.isdir("_posts"):
        print("_posts 폴더가 없습니다. 저장소 루트에서 실행하세요.")
        sys.exit(1)

    if args.og:
        cmd_og(args.include_uncommitted)
        return
    posts = load_posts()
    if args.urls:
        cmd_urls(posts, args.since)
        return
    cmd_report(posts, args.no_csv)


if __name__ == "__main__":
    main()
