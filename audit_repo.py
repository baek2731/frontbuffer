#!/usr/bin/env python3
# =====================================================================
# 🔍 저장소 전수조사 스크립트 (audit_repo.py)
# =====================================================================
# 사용법 (저장소 루트에서):
#   python audit_repo.py
#
# 결과:
#   audit_report.txt     ← 이 파일 1개를 Claude에게 올리면 됩니다.
#   git_inventory.csv    ← 추적 중인 모든 파일의 경로/크기 (선택)
#
# 읽기 전용입니다. 파일을 수정하거나 삭제하지 않습니다. 외부 접속도 없습니다.
# 필요한 것: Python 3.8+ 와 git (추가 패키지 없음)
# =====================================================================

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(".").resolve()
REPORT = "audit_report.txt"
INVENTORY = "git_inventory.csv"
SITE = "https://frontbuffer.net"

BANNED_PHRASES = [
    "has emerged as", "it's worth noting", "in conclusion, it is clear",
    "in today's world", "this article aims to", "let's dive into",
    "it is essential to", "it is crucial to", "delves into", "unparalleled",
    "furthermore", "underscore", "hinges on", "boils down to",
    "enduring appeal", "paramount", "vibrant", "shed light on",
    "revolutionary", "cutting-edge", "innovative", "pushing the boundaries",
    "remarkable", "seamlessly", "comprehensive", "robust", "testament to",
    "meticulous", "commendable", "highly anticipated", "non-negotiable",
    "in this article, we will", "this article covers", "this article explains",
]
BANNED_DOMAINS = [
    "youtube.com", "youtu.be", "reddit.com", "ebay.", "amazon.", "gamerant.com",
    "fextralife", "cnet.com", "phonearena.com", "gsmarena.com", "techradar.com",
    "tomsguide.com", "sammobile.com", "wikipedia.org", "gadgets360.com",
]
NEWS_DOMAINS = [
    "androidauthority.com", "9to5google.com", "theverge.com", "arstechnica.com",
    "eurogamer.net", "pcgamer.com", "windowscentral.com", "engadget.com",
    "techcrunch.com", "tomshardware.com", "digitaltrends.com", "gizmodo.com",
    "wired.com", "androidpolice.com", "xda-developers.com",
]
JUNK_TAGS = {"and", "the", "to", "of", "for", "in", "on", "features", "feature",
             "platform", "z", "foldflip", "overview"}

R = []          # 보고서 줄
COUNTS = Counter()


def out(line=""):
    R.append(line)


def head(title):
    out()
    out("=" * 70)
    out(title)
    out("=" * 70)


def flag(level, msg):
    icon = {"H": "🔴", "M": "🟠", "L": "🟡", "I": "ℹ️ "}[level]
    COUNTS[level] += 1
    out(f"{icon} {msg}")


def read(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


# ───────────────────────── git 파일 목록 ─────────────────────────
def git_files():
    try:
        raw = subprocess.run(
            ["git", "-c", "core.quotepath=false", "ls-files", "-z"],
            capture_output=True, check=True).stdout
        files = [f for f in raw.decode("utf-8", errors="replace").split("\0") if f]
        return files, True
    except Exception:
        files = []
        for p in ROOT.rglob("*"):
            if p.is_file() and ".git" not in p.parts:
                files.append(str(p.relative_to(ROOT)).replace("\\", "/"))
        return files, False


def fsize(f):
    try:
        return (ROOT / f).stat().st_size
    except Exception:
        return -1


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


# ───────────────────────── front matter 파서 ─────────────────────────
def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        v = v[1:-1]
        v = v.replace("''", "'")
    return v


def parse_post(path):
    text = read(path)
    fm, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            block, body = text[3:end], text[end + 4:]
            in_header = False
            for line in block.splitlines():
                if re.match(r"^header:\s*$", line):
                    in_header = True
                    continue
                if in_header and re.match(r"^\s+image:\s*(.+)$", line):
                    fm["header_image"] = unquote(re.match(r"^\s+image:\s*(.+)$", line).group(1))
                    continue
                if in_header and not line.startswith(" "):
                    in_header = False
                m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
                if m:
                    fm[m.group(1)] = unquote(m.group(2))
    return fm, body, text


def post_url(name, fm):
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$", name)
    if not m:
        return None, None, None
    date, slug_raw = m.group(1), m.group(2)
    if fm.get("permalink"):
        return date, slug_raw, SITE + fm["permalink"]
    cats = fm.get("categories", "")
    cat = re.sub(r"[\[\]'\"]", "", cats).split(",")[0].strip() or "?"
    return date, slug_raw, f"{SITE}/{cat}/{slug_raw.rstrip('-')}/"


# ───────────────────────── 점검 구간 ─────────────────────────
def section_inventory(files, is_git):
    head("1. 인벤토리")
    total = sum(max(fsize(f), 0) for f in files)
    out(f"추적 파일 수: {len(files)}  / 총 크기: {human(total)}  (git 사용: {is_git})")

    with open(INVENTORY, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["path", "bytes"])
        for f in files:
            w.writerow([f, fsize(f)])

    by_top = defaultdict(lambda: [0, 0])
    for f in files:
        top = f.split("/")[0] if "/" in f else "(루트)"
        by_top[top][0] += 1
        by_top[top][1] += max(fsize(f), 0)
    out("\n[최상위 폴더별 파일 수 / 크기]")
    for top, (n, sz) in sorted(by_top.items(), key=lambda x: -x[1][1]):
        out(f"  {top:<28} {n:>5}개  {human(sz):>9}")

    out("\n[루트 파일 목록]")
    for f in sorted(x for x in files if "/" not in x):
        out(f"  {f}  ({human(max(fsize(f), 0))})")

    out("\n[확장자별 개수]")
    ext = Counter(Path(f).suffix.lower() or "(없음)" for f in files)
    out("  " + ", ".join(f"{k}:{v}" for k, v in ext.most_common(15)))

    out("\n[가장 큰 파일 15개]")
    for f in sorted(files, key=lambda x: -fsize(x))[:15]:
        out(f"  {human(max(fsize(f), 0)):>9}  {f}")
    for f in files:
        if fsize(f) > 5 * 1024 * 1024:
            flag("M", f"5MB 초과 파일이 추적 중: {f} ({human(fsize(f))})")


def section_hygiene(files):
    head("2. 저장소 위생")
    pyc = [f for f in files if "__pycache__" in f or f.endswith(".pyc")]
    if pyc:
        flag("M", f"컴파일 파일(.pyc/__pycache__) {len(pyc)}개가 추적 중 → git rm --cached 후 .gitignore 추가")
    for pat, why in [(r"(^|/)\.env($|\.)", ".env 파일"), (r"\.DS_Store$|Thumbs\.db$", "OS 임시 파일"),
                     (r"node_modules/", "node_modules"), (r"\.(zip|7z|rar)$", "압축 파일")]:
        hits = [f for f in files if re.search(pat, f)]
        if hits:
            flag("M" if ".env" in why else "L", f"{why} 추적 중 {len(hits)}개: {', '.join(hits[:5])}")

    gi = read(".gitignore")
    if not gi:
        flag("M", ".gitignore 가 없음")
    else:
        for need in ["__pycache__", ".env"]:
            if need not in gi:
                flag("L", f".gitignore 에 '{need}' 항목 없음")

    # 워크플로우 밖에 있는 yml
    wf_dir = ".github/workflows/"
    stray = [f for f in files if f.endswith((".yml", ".yaml")) and not f.startswith(wf_dir)
             and re.search(r"^\s*on:|^\s*jobs:", read(f), re.M)]
    for f in stray:
        base = Path(f).name
        twin = wf_dir + base
        if twin in files:
            same = hashlib.md5(read(f).encode()).hexdigest() == hashlib.md5(read(twin).encode()).hexdigest()
            flag("M", f"워크플로우 사본이 밖에 있음: {f} (실제 사용: {twin}, 내용 {'동일' if same else '다름'}) → 삭제 권장")
        else:
            flag("H", f"워크플로우처럼 보이는 파일이 .github/workflows 밖에 있음: {f} → 실행되지 않음")

    # 같은 이름의 파일이 여러 폴더에 있는 경우 (py/yml)
    names = defaultdict(list)
    for f in files:
        if f.endswith((".py", ".yml")):
            names[Path(f).name].append(f)
    for n, lst in names.items():
        if len(lst) > 1 and not all(x.startswith(wf_dir) for x in lst):
            out(f"ℹ️  같은 이름 파일 여러 곳: {n} → {lst}")

    # 루트 py 중 어디에서도 쓰이지 않는 것
    py_root = [f for f in files if f.endswith(".py") and "/" not in f]
    corpus = "\n".join(read(f) for f in files if f.endswith((".py", ".yml")))
    for f in py_root:
        mod = Path(f).stem
        refs = len(re.findall(rf"\b{re.escape(mod)}\b", corpus)) - len(re.findall(rf"\b{re.escape(mod)}\b", read(f)))
        if refs <= 0:
            out(f"ℹ️  어디에서도 참조되지 않는 스크립트: {f} (수동 도구면 정상)")


def section_workflows(files):
    head("3. 워크플로우")
    wfs = sorted(f for f in files if f.startswith(".github/workflows/") and f.endswith((".yml", ".yaml")))
    all_secrets = set()
    for f in wfs:
        t = read(f)
        name = (re.search(r"^name:\s*(.+)$", t, re.M) or [None, "?"])[1].strip("\"' ")
        crons = re.findall(r"cron:\s*['\"]([^'\"]+)['\"]", t)
        disp = "workflow_dispatch" in t
        secrets = sorted(set(re.findall(r"secrets\.([A-Z0-9_]+)", t)))
        all_secrets |= set(secrets)
        scripts = sorted(set(re.findall(r"python\s+([\w./-]+\.py)", t)))
        out(f"\n• {f}  ({name})")
        out(f"    cron: {crons or '없음'} | 수동실행: {'O' if disp else 'X'} | secrets: {secrets or '없음'}")
        out(f"    실행 스크립트: {scripts or '없음'}")
        if "permissions:" not in t and ("git push" in t):
            flag("L", f"{f}: git push 를 하지만 permissions 선언이 없음 (저장소 기본 권한에 의존)")
        if "git push" in t and "pull --rebase" not in t:
            flag("L", f"{f}: push 전에 pull --rebase 가 없음 (동시 푸시 시 거절될 수 있음)")
        if "concurrency:" not in t and crons:
            out("    ℹ️  concurrency 미설정 (같은 워크플로우 중복 실행 가능)")
        for s in scripts:
            if s not in files and s.lstrip("./") not in files:
                flag("H", f"{f}: 실행하는 스크립트가 저장소에 없음 → {s}")
        for m in re.finditer(r"cron:\s*['\"]([^'\"]+)['\"]", t):
            c = m.group(1).split()
            if len(c) == 5 and c[4] not in ("*", "?"):
                out(f"    ℹ️  특정 요일에만 실행: cron '{m.group(1)}'")
    out(f"\n[워크플로우에서 쓰는 secrets 전체] {sorted(all_secrets)}")
    out("→ GitHub Settings > Secrets and variables > Actions 에 모두 등록돼 있는지 확인하세요.")
    out("  (GITHUB_TOKEN 은 자동 제공)")


def section_site(files):
    head("4. 사이트 설정")
    for f, level in [("_config.yml", "H"), ("Gemfile", "L"), ("robots.txt", "L"), ("ads.txt", "I"), ("CNAME", "L")]:
        if f in files:
            out(f"  ✓ {f}")
        else:
            flag(level, f"{f} 없음")
    keys = [f for f in files if re.match(r"^[0-9a-f]{32}\.txt$", f)]
    out(f"  IndexNow 키 파일: {keys or '없음'}")
    wf_text = "\n".join(read(f) for f in files if f.startswith(".github/workflows/"))
    for k in re.findall(r"\b([0-9a-f]{32})\b", wf_text):
        if f"{k}.txt" not in files:
            flag("M", f"워크플로우의 IndexNow 키 {k} 와 같은 이름의 .txt 파일이 저장소 루트에 없음")
            break

    cfg = read("_config.yml")
    if cfg:
        _pm = re.search(r"^permalink:\s*(.+)$", cfg, re.M)
        out("  permalink: " + (_pm.group(1) if _pm else "?"))
        plugins = re.findall(r"^\s+-\s+(jekyll-[\w-]+)", cfg, re.M)
        out(f"  plugins: {plugins}")
        if "research_data" not in cfg:
            flag("H", "_config.yml 의 exclude 에 research_data/ 가 없음 → 초안/프롬프트가 사이트로 발행될 수 있음")
        if "redirect-from" not in cfg:
            out("  ℹ️  jekyll-redirect-from 없음 → URL 변경 시 옛 주소는 404")

    pages = [f for f in files if f.startswith("_pages/")]
    out(f"  _pages: {[Path(p).name for p in pages]}")
    page_text = " ".join(read(p).lower() + p.lower() for p in pages)
    for need in ["about", "privacy", "disclosure", "contact"]:
        if need not in page_text:
            flag("M" if need in ("contact", "about") else "L", f"'{need}' 페이지로 보이는 파일이 _pages 에 없음 (애드센스/신뢰 요건)")
    big = [f for f in files if f.startswith(("social_output/", "assets/")) and f.endswith((".png", ".jpg", ".jpeg"))]
    if big:
        out(f"  이미지 추적: {len(big)}개 / {human(sum(max(fsize(x), 0) for x in big))} (저장소 용량 증가 요인)")


def section_posts(files):
    head("5. 글(_posts) 점검")
    posts = sorted(f for f in files if f.startswith("_posts/") and f.endswith(".md"))
    out(f"글 수: {len(posts)}")
    if not posts:
        return {}

    urls = defaultdict(list)
    titles = defaultdict(list)
    existing_names = {Path(p).stem for p in posts}
    url_map = {}
    per_file = defaultdict(list)

    for p in posts:
        name = Path(p).name
        fm, body, raw = parse_post(p)
        date, slug_raw, url = post_url(name, fm)
        if not url:
            flag("M", f"{name}: 파일명이 YYYY-MM-DD-slug.md 형식이 아님")
            continue
        url_map[name] = url
        urls[url].append(name)
        t = fm.get("title", "")
        if not t:
            flag("H", f"{name}: title 없음")
        else:
            titles[t.lower()].append(name)
            if len(t) > 70:
                per_file[name].append(f"제목 {len(t)}자(70자 초과)")
        ex = fm.get("excerpt", "")
        if not ex:
            per_file[name].append("excerpt 없음")
        else:
            if len(ex) < 110:
                per_file[name].append(f"excerpt 짧음({len(ex)}자)")
            if len(ex) > 170:
                per_file[name].append(f"excerpt 김({len(ex)}자)")
            if ex.rstrip().endswith("…") or ex.rstrip().endswith("..."):
                per_file[name].append("excerpt 가 …로 잘림")
            if re.search(r"[*`\[\]]", ex):
                per_file[name].append("excerpt 에 마크다운 기호")
            if ex.startswith("layout"):
                per_file[name].append("excerpt 가 'layout...' (front matter 버그)")
        tags = re.findall(r"[\"']([^\"']+)[\"']", fm.get("tags", ""))
        junk = [x for x in tags if x.lower() in JUNK_TAGS or len(x) < 2 or x.isdigit()]
        if junk:
            per_file[name].append(f"의미 없는 태그 {junk}")
        if not tags:
            per_file[name].append("태그 없음")
        if not fm.get("categories"):
            per_file[name].append("categories 없음")
        if date and fm.get("date") and not fm["date"].startswith(date):
            per_file[name].append(f"front matter 날짜({fm['date'][:10]}) ≠ 파일명 날짜({date})")
        img = fm.get("header_image", "")
        if not img:
            per_file[name].append("header.image 없음 (OG 이미지 미연결)")
        else:
            m = re.search(r"/posts/([^/]+)/", img)
            if m and m.group(1) != slug_raw:
                per_file[name].append(f"header 이미지 경로 슬러그 불일치({m.group(1)} ≠ {slug_raw})")
        if fm.get("sitemap", "").lower() == "false":
            per_file[name].append("sitemap: false")
        if fm.get("canonical_url"):
            per_file[name].append(f"canonical_url → {fm['canonical_url'][:70]}")
        for ph in ["[INTERNAL LINK", "[cite", "[NEEDS VERIFICATION", "[Source:", "판정 요약", "[AFFILIATE LINK"]:
            if ph in raw:
                per_file[name].append(f"플레이스홀더 잔존 '{ph}'")
        if re.search(r"[가-힣]", body):
            per_file[name].append("본문에 한글 포함")
        low = re.sub(r"https?://\S+", " ", re.sub(r"\]\([^)]*\)", "]", raw)).lower()
        hits = sorted({b for b in BANNED_PHRASES if b in low})
        if hits:
            per_file[name].append(f"금지 표현 {hits}")
        links = re.findall(r"\]\((https?://[^)\s]+)\)", raw)
        root_links = [l for l in links if re.fullmatch(r"https?://[^/]+/?", l)]
        root_links = [l for l in root_links if any(d in l.lower() for d in NEWS_DOMAINS)]
        if root_links:
            per_file[name].append(f"뉴스 사이트 루트 도메인 링크(개별 기사 URL 필요) {sorted(set(root_links))[:3]}")
        bad = sorted({d for l in links for d in BANNED_DOMAINS if d in l.lower()})
        if bad:
            per_file[name].append(f"금지 출처 도메인 {bad}")
        for ref in re.findall(r"\{%\s*post_url\s+([^\s%]+)\s*%\}", raw):
            if ref not in existing_names:
                flag("H", f"{name}: post_url 대상 파일이 없음 → {ref} (Jekyll 빌드 실패 원인)")

    for u, names in urls.items():
        if len(names) > 1:
            flag("H", f"같은 URL을 쓰는 글 {len(names)}개 (한쪽만 보임): {u} ← {names}")
    for t, names in titles.items():
        if len(names) > 1:
            flag("M", f"같은 제목의 글: {names}")

    out(f"\n[글별 지적 사항] ({len(per_file)}개 글)")
    cnt = Counter()
    for name in sorted(per_file):
        for item in per_file[name]:
            cnt[re.sub(r"[\[\{(].*", "", item).strip()] += 1
        out(f"  - {name}")
        for item in per_file[name]:
            out(f"      · {item}")
    out("\n[지적 유형별 개수]")
    for k, v in cnt.most_common():
        out(f"  {v:>3}  {k}")
    return url_map


def section_data(files, url_map):
    head("6. 데이터 파일 일관성 (posts.json / content_pipeline.json)")
    live = {u.rstrip("/") for u in url_map.values()}

    if "posts.json" in files:
        try:
            data = json.loads(read("posts.json"))
            items = data.get("posts", [])
            out(f"posts.json: {len(items)}건")
            missing = [p for p in items if p.get("live_url", "").rstrip("/") not in live]
            if missing:
                flag("I", f"posts.json 에는 있지만 현재 _posts 로 확인되지 않는 항목 {len(missing)}건 "
                          f"(삭제한 중복 글이면 정상, 재발행 방지 용도)")
                for p in missing[:15]:
                    out(f"      - {p.get('date', '?')} {p.get('title', '')[:70]}")
            posted = {p.get("live_url", "").rstrip("/") for p in items}
            unregistered = [n for n, u in url_map.items() if u.rstrip("/") not in posted]
            if unregistered:
                flag("L", f"_posts 에는 있지만 posts.json 에 없는 글 {len(unregistered)}개 (수동 수정/이름 변경 글일 수 있음)")
                for n in unregistered[:20]:
                    out(f"      - {n}")
        except Exception as e:
            flag("H", f"posts.json 읽기 실패: {e}")
    else:
        flag("H", "posts.json 없음")

    if "content_pipeline.json" in files:
        try:
            pipe = json.loads(read("content_pipeline.json"))
        except Exception as e:
            flag("H", f"content_pipeline.json 읽기 실패: {e}")
            return
        out(f"\ncontent_pipeline.json: 버전 {pipe.get('_version')} / 최종 갱신 {pipe.get('_last_updated')}")
        wk = pipe.get("weekly_selections", {})
        st = Counter()
        stale = []
        for week, sels in wk.items():
            for s in sels:
                st[s.get("status", "?")] += 1
                if s.get("status") == "candidate":
                    stale.append((week, s.get("cluster_name"), s.get("content_type")))
        out(f"weekly_selections: {len(wk)}주차 / 상태별 {dict(st)}")
        if stale:
            out(f"  candidate(대기) {len(stale)}건:")
            for w, n, c in stale[:30]:
                out(f"      - {w} {n} [{c}]")
        pub = pipe.get("published", [])
        pend = [p for p in pub if str(p.get("url", "pending")).lower() in ("pending", "", "none")]
        out(f"published: {len(pub)}건 (URL 미기록 {len(pend)}건)")
        if pend:
            flag("L", f"published 항목 중 URL 이 pending 인 것 {len(pend)}건")
        miss = [p for p in pub if p.get("url", "").startswith("http") and p["url"].rstrip("/") not in live]
        if miss:
            flag("L", f"published 의 URL 중 현재 사이트에 없는 것 {len(miss)}건 (삭제/이름 변경 글)")
            for p in miss[:10]:
                out(f"      - {p.get('url')}")
        hubs = pipe.get("hub_clusters", {})
        pending_spokes = {k: [s for s, v in h.get("spoke_urls", {}).items() if str(v).lower() in ("pending", "")]
                          for k, h in hubs.items()}
        pending_spokes = {k: v for k, v in pending_spokes.items() if v}
        out(f"hub_clusters: {len(hubs)}개 / 스포크 URL pending 이 있는 클러스터 {len(pending_spokes)}개")

        def toks(s):
            return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2}
        names = list(hubs.keys())
        pairs = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = toks(names[i]), toks(names[j])
                if a and b and len(a & b) / len(a | b) >= 0.5:
                    pairs.append((names[i], names[j]))
        if pairs:
            flag("M", f"이름이 비슷한 허브 클러스터 {len(pairs)}쌍 (같은 주제 중복 생성의 원인)")
            for a, b in pairs[:25]:
                out(f"      - {a}  ≈  {b}")

        # 기획안 이상 징후
        def _slug(t):
            t = re.sub(r"[^\w\s-]", "", t.lower().strip())
            return re.sub(r"[\s_]+", "-", t)[:60]
        mism = []
        dup_key = defaultdict(list)
        for week, sels in wk.items():
            for s_ in sels:
                fld = (s_.get("folder") or "").lower()
                if fld and fld != _slug(s_.get("cluster_name", "")):
                    mism.append((week, s_.get("cluster_name"), fld))
                dup_key[(week, s_.get("cluster_name"), (s_.get("content_type") or "").upper())].append(s_)
        out(f"\n파일 ID(folder)와 클러스터 이름 슬러그가 다른 기획안: {len(mism)}건")
        out("  → 예전 publish_one.py 는 이런 글의 발행 상태를 기록하지 못해 같은 기획안이 재작성됐음 (수정본 적용 필요)")
        dups = {k: v for k, v in dup_key.items() if len(v) > 1}
        if dups:
            flag("L", f"같은 주차/클러스터/유형 기획안이 2개 이상인 경우 {len(dups)}건")
            for (w, n, c), v in list(dups.items())[:10]:
                out(f"      - {w} {n} [{c}]: 상태 {[x.get('status') for x in v]}")
        for w, n, c in stale:
            if w < "2026-W38":
                flag("L", f"오래된 candidate: {w} {n} [{c}] (3주 이상 대기)")
    else:
        flag("H", "content_pipeline.json 없음")


def section_final(files):
    head("7. 발행 대기(final) / 보류(hold) / 폐기(rejected)")
    base = "research_data/write/"
    for d in ("final", "hold", "rejected"):
        md = sorted(f for f in files if f.startswith(base + d + "/") and f.endswith(".md"))
        rr = sorted(f for f in files if f.startswith(base + d + "/") and Path(f).name.startswith("review_report_"))
        out(f"{d}: 글 {len(md)}개 / review_report {len(rr)}개")
        for f in md:
            t = ""
            for line in read(f).splitlines():
                if line.startswith("# "):
                    t = line[2:].strip()
                    break
            warn = []
            raw = read(f)
            for ph in ["[INTERNAL LINK", "[cite", "판정 요약", "NEEDS VERIFICATION"]:
                if ph in raw:
                    warn.append(ph)
            out(f"   - {Path(f).name}: {t[:70]} {('⚠ ' + ','.join(warn)) if warn else ''}")
        stems = {Path(f).stem for f in md}
        orphan = [f for f in rr if Path(f).stem.replace("review_report_", "", 1) not in stems]
        if orphan and d == "final":
            flag("L", f"final 에 짝 없는 review_report {len(orphan)}개 (발행 후 남은 잔재, 삭제 가능)")
    pub = [f for f in files if f.startswith(base + "published/") and f.endswith(".md")]
    out(f"published(아카이브): {len(pub)}개")


def section_og(files):
    head("8. OG 이미지(social_output) 점검")
    posts = [Path(f).name for f in files if f.startswith("_posts/") and f.endswith(".md")]
    have = {f.split("/")[1] for f in files if f.startswith("social_output/") and f.endswith("og.png")}
    missing = []
    for n in posts:
        m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$", n)
        if m and m.group(1) not in have:
            missing.append(n)
    out(f"og.png 추적: {len(have)}개 / 글 {len(posts)}개")
    if missing and have:
        flag("L", f"social_output 에 og.png 가 없는 글 {len(missing)}개 (R2 에만 있을 수 있음)")
        for n in missing[:15]:
            out(f"      - {n}")


def main():
    files, is_git = git_files()
    head(f"저장소 전수조사 — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    out(f"경로: {ROOT}")
    section_inventory(files, is_git)
    section_hygiene(files)
    section_workflows(files)
    section_site(files)
    url_map = section_posts(files)
    section_data(files, url_map)
    section_final(files)
    section_og(files)

    head("요약")
    out(f"🔴 높음 {COUNTS['H']}건 / 🟠 중간 {COUNTS['M']}건 / 🟡 낮음 {COUNTS['L']}건 / ℹ️ 참고 {COUNTS['I']}건")
    Path(REPORT).write_text("\n".join(R) + "\n", encoding="utf-8")
    print(f"\n✅ 완료: {REPORT} ({len(R)}줄), {INVENTORY}")
    print(f"   🔴 {COUNTS['H']}  🟠 {COUNTS['M']}  🟡 {COUNTS['L']}  ℹ️ {COUNTS['I']}")
    print(f"   → {REPORT} 파일을 Claude에게 올려 주세요.")


if __name__ == "__main__":
    main()
