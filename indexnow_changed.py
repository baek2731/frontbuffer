#!/usr/bin/env python3
# =====================================================================
# 바뀐 글을 Bing 등에 자동으로 알리기 (indexnow_changed.py)
# =====================================================================
# .github/workflows/indexnow_on_push.yml 이 푸시마다 실행합니다. 이번 푸시에서 추가되거나 바뀐
# _posts/*.md, _pages/*.md 의 주소를 계산해 IndexNow 로 한 번에 제출합니다.
# 새 글 발행(Step 4)은 자체적으로 알리고, GitHub 봇의 푸시는 이 워크플로를 실행하지 않습니다.
#
# 직접 써 볼 때 (저장소 폴더에서, 제출하지 않고 주소만 확인):
#   python indexnow_changed.py --before HEAD~1 --after HEAD --dry-run
#   python indexnow_changed.py --urls "https://frontbuffer.net/tech/a/ https://frontbuffer.net/gaming/b/" --dry-run
# 커밋 메시지에 [skip indexnow] 가 있으면 제출하지 않습니다.
# 주소 규칙은 post_status.py 와 같습니다 (permalink 가 있으면 그것, 없으면 /카테고리/날짜를 뗀 파일 이름/).
# 종료 코드: 0 정상(제출했거나 보낼 것이 없음), 1 제출 실패(Actions 에서 빨간색으로 보임)
# =====================================================================
import argparse, json, os, re, subprocess, sys, urllib.error, urllib.request

HOST = "frontbuffer.net"
DEFAULT_BASE_URL = "https://frontbuffer.net"
KEY = os.environ.get("INDEXNOW_KEY", "598f6bef9c054f238ee360ceb0374da3")     # 공개 키 (사이트 루트의 키 파일과 같음)
ENDPOINT = os.environ.get("INDEXNOW_ENDPOINT", "https://api.indexnow.org/IndexNow")
MAX_URLS = 200
SKIP_PATHS = {"/tags/", "/categories/"}          # robots 로 막은 목록 페이지는 알리지 않음

ap = argparse.ArgumentParser()
ap.add_argument("--before", default="")
ap.add_argument("--after", default="HEAD")
ap.add_argument("--urls", default="", help="공백·줄바꿈으로 구분한 주소를 직접 제출")
ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()

def git(*args):
    r = subprocess.run(["git", "-c", "core.quotepath=off", *args], capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip()

def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        v = v[1:-1]
    return v

def front_matter(text):
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    if len(parts) < 3:
        return {}
    fm = {}
    for line in parts[1].splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm

def jekyll_slug(fname):
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", fname)
    if slug.endswith(".md"):
        slug = slug[:-3]
    slug = re.sub(r"[^\w.~!$&'()+,;=@]+", "-", slug)
    return slug.strip("-")

def base_url():
    try:
        t = open("_config.yml", "rb").read().decode("utf-8", "ignore")
        m = re.search(r"^url\s*:\s*[\"']?([^\"'\s]+)", t, flags=re.M)
        if m:
            return m.group(1).rstrip("/")
    except OSError:
        pass
    return DEFAULT_BASE_URL

def url_for(path, base):
    fm = front_matter(open(path, "rb").read().decode("utf-8", "ignore"))
    if unquote(fm.get("sitemap", "")).lower() == "false":
        return ""
    perm = unquote(fm.get("permalink", ""))
    if perm:
        return base + (perm if perm.startswith("/") else "/" + perm)
    cats = [unquote(c) for c in fm.get("categories", "").strip().strip("[]").split(",") if c.strip()]
    if not cats:
        return ""
    return "%s/%s/%s/" % (base, "/".join(cats), jekyll_slug(os.path.basename(path)))

# ---- 어떤 주소를 보낼지 정하기
urls = []
if a.urls.strip():
    urls = [u for u in re.split(r"\s+", a.urls.strip()) if u]
else:
    rc, msg = git("log", "-1", "--pretty=%B", a.after)
    if rc == 0 and "[skip indexnow]" in msg.lower():
        print("커밋 메시지에 [skip indexnow] 가 있어 제출하지 않습니다.")
        sys.exit(0)
    before = a.before.strip()
    if not before or set(before) == {"0"} or git("cat-file", "-e", before + "^{commit}")[0] != 0:
        before = a.after + "^"
    rc, out = git("diff", "--name-only", "--diff-filter=AMR", before, a.after, "--", "_posts/*.md", "_pages/*.md")
    if rc != 0:
        print("변경된 파일 목록을 가져오지 못했습니다:", out)
        sys.exit(1)
    base = base_url()
    for f in [x for x in out.splitlines() if x.strip()]:
        if not os.path.exists(f):
            continue
        u = url_for(f, base)
        if u and not any(u.endswith(p) for p in SKIP_PATHS):
            urls.append(u)

seen, uniq = set(), []
for u in urls:
    if u not in seen:
        seen.add(u); uniq.append(u)
urls = uniq
bad = [u for u in urls if not re.match(r"https://%s/" % re.escape(HOST), u)]
if bad:
    print("다른 도메인의 주소가 섞여 있어 중단합니다:", bad[:3])
    sys.exit(1)
if not urls:
    print("알릴 주소가 없습니다 (바뀐 글이 없거나 목록 페이지뿐).")
    sys.exit(0)
if len(urls) > MAX_URLS:
    print(f"주소가 {len(urls)}개로 한도({MAX_URLS}개)를 넘어 중단합니다. 일괄 수정이라면 필요한 주소만 --urls 로 제출하세요.")
    sys.exit(1)

print(f"제출할 주소 {len(urls)}개:")
for u in urls[:60]:
    print("  ", u)
if len(urls) > 60:
    print(f"   ... 외 {len(urls) - 60}개")
if a.dry_run:
    print("[dry-run] 제출하지 않았습니다.")
    sys.exit(0)

payload = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls}).encode("utf-8")
req = urllib.request.Request(ENDPOINT, data=payload, method="POST", headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"제출 {len(urls)}개 → HTTP {r.status} (200 또는 202 이면 접수됨)")
        sys.exit(0)
except urllib.error.HTTPError as e:
    meaning = {400: "요청 형식 오류", 403: "키 불일치", 422: "주소가 호스트와 맞지 않음", 429: "너무 많은 요청, 나중에 다시"}.get(e.code, "")
    print(f"제출 실패 {len(urls)}개 → HTTP {e.code} {meaning}")
except Exception as e:
    print(f"제출 실패: {e}")
sys.exit(1)
