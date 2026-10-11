#!/usr/bin/env python3
# =====================================================================
# 🌐 라이브 사이트 전수 점검 (site_check.py)
# =====================================================================
# 실제 배포된 사이트(https://frontbuffer.net)를 sitemap.xml 기준으로 전부 열어서 점검한다.
# 읽기 전용이며 파일을 수정하지 않는다. 추가 패키지 없음 (Python 3.8+).
#
# 사용법 (어느 폴더에서나):
#   python site_check.py                 ← 사이트 전체 점검 (약 2~4분)
#   python site_check.py --external      ← 외부 링크 상태도 확인 (더 오래 걸림)
#   python site_check.py --base https://frontbuffer.net
#
# 결과: site_report.txt  ← 이 파일을 Claude에게 올려 주세요.
#
# 점검 항목:
#   페이지: HTTP 상태, canonical, 제목 길이, meta description 길이, og:image 접근, h1 개수,
#           본문 단어 수(얇은 글), 금지 표현, 플레이스홀더 잔존, 한글 포함
#   링크  : 내부 링크 404, 금지 출처 도메인, 뉴스 사이트 루트 도메인 링크, 외부 링크 상태(--external)
#   사이트: 같은 제목/설명을 쓰는 페이지, sitemap 에 있는 주소의 접근 가능 여부
# =====================================================================

import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; frontbuffer-site-check/1.0)"
TIMEOUT = 20
BANNED_PHRASES = [
    "has emerged as", "it's worth noting", "in conclusion, it is clear", "in today's world",
    "this article aims to", "let's dive into", "it is essential to", "it is crucial to",
    "delves into", "unparalleled", "furthermore", "underscore", "hinges on", "boils down to",
    "enduring appeal", "paramount", "vibrant", "shed light on", "revolutionary", "cutting-edge",
    "innovative", "pushing the boundaries", "remarkable", "seamlessly", "comprehensive",
    "robust", "testament to", "meticulous", "commendable", "highly anticipated",
    "non-negotiable", "this article covers", "this article explains",
]
BANNED_DOMAINS = ["youtube.com", "youtu.be", "reddit.com", "ebay.", "amazon.", "gamerant.com",
                  "fextralife", "cnet.com", "phonearena.com", "gsmarena.com", "techradar.com",
                  "tomsguide.com", "sammobile.com", "wikipedia.org", "gadgets360.com"]
NEWS_DOMAINS = ["androidauthority.com", "9to5google.com", "theverge.com", "arstechnica.com",
                "eurogamer.net", "pcgamer.com", "windowscentral.com", "engadget.com",
                "techcrunch.com", "tomshardware.com", "digitaltrends.com", "gizmodo.com",
                "wired.com", "androidpolice.com", "xda-developers.com"]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta = {}
        self.canonical = ""
        self.h1 = 0
        self.links = []
        self.text = []
        self._in_title = False
        self._skip = 0
        self._in_article = 0
        self.article_text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag in ("script", "style", "noscript"):
            self._skip += 1
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key and a.get("content") is not None:
                self.meta[key.lower()] = a["content"]
        elif tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = a.get("href", "")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag in ("article", "main"):
            self._in_article += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("script", "style", "noscript"):
            self._skip = max(0, self._skip - 1)
        elif tag in ("article", "main"):
            self._in_article = max(0, self._in_article - 1)

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self._skip:
            self.text.append(data)
            if self._in_article:
                self.article_text.append(data)


def fetch(url, method="GET", read=True):
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read().decode("utf-8", errors="replace") if read and method == "GET" else ""
            return r.status, r.geturl(), body
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:
        return 0, url, str(e)[:80]


def main():
    base = "https://frontbuffer.net"
    external = "--external" in sys.argv
    if "--base" in sys.argv:
        base = sys.argv[sys.argv.index("--base") + 1].rstrip("/")
    host = urllib.parse.urlparse(base).netloc
    R, issues = [], Counter()

    icons = {"H": "🔴", "M": "🟠", "L": "🟡", "I": "ℹ️ "}

    def flag(level, msg):
        issues[level] += 1
        R.append(icons[level] + " " + msg)

    status, _, xml = fetch(base + "/sitemap.xml")
    if status != 200:
        print(f"❌ sitemap.xml 을 열 수 없습니다 (HTTP {status})")
        sys.exit(1)
    urls = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)
    urls = [u for u in urls if u.rstrip("/") != base]
    print(f"sitemap 주소 {len(urls)}개 점검 시작...")

    pages = {}
    all_links = defaultdict(set)      # 링크 → 그 링크를 포함한 페이지들
    def work(u):
        time.sleep(0.15)
        st, final, html = fetch(u)
        return u, st, final, html
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(work, urls))

    titles, descs = defaultdict(list), defaultdict(list)
    for u, st, final, html in results:
        path = urllib.parse.urlparse(u).path
        if st != 200:
            flag("H", f"{path}: HTTP {st} (sitemap 에는 있지만 열리지 않음)")
            continue
        p = Page()
        try:
            p.feed(html)
        except Exception:
            flag("M", f"{path}: HTML 해석 실패")
            continue
        title = re.sub(r"\s*[-–|]\s*Frontbuffer\s*$", "", p.title.strip())
        desc = p.meta.get("description", "")
        og_img = p.meta.get("og:image", "")
        body = " ".join(p.article_text or p.text)
        words = len(re.findall(r"\w+", body))
        pages[u] = (title, desc, words)
        titles[title.lower()].append(path)
        if desc:
            descs[desc].append(path)

        if final.rstrip("/") != u.rstrip("/"):
            flag("L", f"{path}: 다른 주소로 이동됨 → {final}")
        if p.canonical.rstrip("/") != u.rstrip("/"):
            flag("M", f"{path}: canonical 불일치 ({p.canonical or '없음'})")
        if not title:
            flag("H", f"{path}: title 없음")
        elif len(title) > 70:
            flag("L", f"{path}: 제목 {len(title)}자 (70자 초과)")
        if not desc:
            flag("M", f"{path}: meta description 없음")
        elif len(desc) < 110:
            flag("L", f"{path}: meta description 짧음 ({len(desc)}자)")
        elif len(desc) > 160:
            flag("L", f"{path}: meta description 김 ({len(desc)}자)")
        if desc.endswith(("…", "...")):
            flag("L", f"{path}: meta description 이 잘림")
        if not og_img:
            flag("M", f"{path}: og:image 없음")
        if p.h1 != 1:
            flag("L", f"{path}: h1 이 {p.h1}개")
        if words < 350:
            flag("L", f"{path}: 본문 {words}단어 (얇은 글)")
        low = body.lower()
        hits = sorted({b for b in BANNED_PHRASES if b in low})
        if hits:
            flag("L", f"{path}: 금지 표현 {hits}")
        for ph in ("[INTERNAL LINK", "NEEDS VERIFICATION", "[cite", "판정 요약"):
            if ph in body:
                flag("H", f"{path}: 플레이스홀더 노출 '{ph}'")
        if re.search(r"[가-힣]", body):
            flag("M", f"{path}: 본문에 한글 포함")

        for href in p.links:
            href = href.split("#")[0].strip()
            if not href or href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            full = urllib.parse.urljoin(u, href)
            netloc = urllib.parse.urlparse(full).netloc
            if netloc == host:
                all_links[full].add(path)
            else:
                dom = netloc.lower()
                if any(b in dom for b in BANNED_DOMAINS):
                    flag("M", f"{path}: 금지 출처 링크 → {full[:80]}")
                if any(n in dom for n in NEWS_DOMAINS) and re.fullmatch(r"https?://[^/]+/?", full):
                    flag("M", f"{path}: 뉴스 사이트 루트 도메인 링크 → {full}")
                if external:
                    all_links[full].add(path)

    for t, ps in titles.items():
        if len(ps) > 1:
            flag("M", f"같은 제목의 페이지: {ps}")
    for d, ps in descs.items():
        if len(ps) > 1:
            flag("L", f"같은 meta description 을 쓰는 페이지: {ps}")

    # 링크 상태 (내부는 항상, 외부는 --external)
    check = [l for l in all_links if urllib.parse.urlparse(l).netloc == host or external]
    done_pages = set(urls)
    check = [l for l in check if l not in done_pages and l.rstrip("/") not in {x.rstrip("/") for x in done_pages}]
    print(f"링크 {len(check)}개 상태 확인...")
    def lw(l):
        time.sleep(0.1)
        st, _, _ = fetch(l, method="HEAD" if urllib.parse.urlparse(l).netloc != host else "GET", read=False)
        if st in (403, 405, 0) and urllib.parse.urlparse(l).netloc != host:
            st, _, _ = fetch(l, method="GET", read=False)
        return l, st
    with ThreadPoolExecutor(max_workers=6) as ex:
        for l, st in ex.map(lw, check):
            internal = urllib.parse.urlparse(l).netloc == host
            if st == 404 or (internal and st not in (200, 301, 302)):
                flag("H" if internal else "M", f"깨진 링크 HTTP {st}: {l[:100]}  ← {sorted(all_links[l])[:3]}")
            elif st == 0 and not internal:
                flag("L", f"외부 링크 응답 없음: {l[:100]}")
            elif st >= 400 and not internal and st not in (401, 403, 429):
                flag("L", f"외부 링크 HTTP {st}: {l[:100]}")

    # 보고서
    head = [f"라이브 사이트 점검 — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            f"대상: {base}  /  sitemap 주소 {len(urls)}개, 열린 페이지 {len(pages)}개",
            f"🔴 {issues['H']}  🟠 {issues['M']}  🟡 {issues['L']}", ""]
    wc = sorted(((w, u) for u, (_, _, w) in pages.items()))
    summary = ["[본문 단어 수 하위 8]"] + [f"  {w:>5}  {urllib.parse.urlparse(u).path}" for w, u in wc[:8]]
    typ = Counter(re.sub(r"[:(\[\{].*", "", line[2:].split(": ", 1)[-1])[:28] for line in R)
    sumtype = ["", "[지적 유형별 개수]"] + [f"  {v:>3}  {k}" for k, v in typ.most_common(12)]
    with open("site_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(head + R + [""] + summary + sumtype) + "\n")
    print(f"\n✅ 완료: site_report.txt  🔴 {issues['H']}  🟠 {issues['M']}  🟡 {issues['L']}")
    print("   → site_report.txt 를 Claude에게 올려 주세요.")


if __name__ == "__main__":
    main()
