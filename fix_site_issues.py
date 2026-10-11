#!/usr/bin/env python3
# =====================================================================
# 🛠️ 라이브 점검(site_report.txt) 지적 사항 일괄 수정 (fix_site_issues.py)
# =====================================================================
# 처리 항목:
#   1. 깨진 내부 링크: samsung-health-data-ecosystem_hub → samsung-health-data-ecosystem
#      (그리고 연달아 중복된 "Want the full picture?" 푸터 정리)
#   2. 금지 출처 링크(Wikipedia, TechRadar, GSMArena 등)와 뉴스 사이트 루트 도메인 링크 제거
#        - Sources 목록의 해당 줄 삭제 / 본문 속 링크는 글자만 남기고 링크 해제
#   3. 제목이 70자를 넘는 글의 제목 단축 (URL은 바뀌지 않음)
#   4. 금지 표현(comprehensive, robust, cutting-edge, delves into, hinges on,
#      underscore, vibrant)을 평범한 표현으로 교체
#   5. 156자를 넘어 목록에서 "..."로 잘리는 excerpt 를 150자 이하로 정리
#   6. About/Disclosure/Privacy 페이지의 meta description 추가
#
# 사용법 (저장소 루트에서):
#   python fix_site_issues.py            ← 미리보기 (파일 수정 없음)
#   python fix_site_issues.py --apply    ← 적용
# 끝에 출력되는 날짜 목록으로 OG 이미지를 재생성하세요 (제목·excerpt 가 이미지에 들어갑니다).
# =====================================================================

import re
import sys
from pathlib import Path

POSTS = Path("_posts")
PAGES = Path("_pages")
APPLY = "--apply" in sys.argv

# ── 1) 제목 단축표 (옛 제목 → 새 제목, 모두 70자 이하) ─────────────────────
TITLES = {
    "Steam Machine Overheating and Red Light: Is It a BIOS Bug or Real Issue":
        "Steam Machine Overheating and Red Light: BIOS Bug or Real Issue?",
    "How to Back Up Samsung Health Data Before Switching Phones or Deleting Your Account":
        "How to Back Up Samsung Health Data Before Switching or Deleting",
    "Best Manifest V3 Chrome Extension Alternatives: uBlock Origin Lite and More (2026)":
        "Best Manifest V3 Alternatives: uBlock Origin Lite and More (2026)",
    "Samsung Secure Folder vs Google Files Safe Folder: Privacy Features Comparison":
        "Samsung Secure Folder vs Google Files Safe Folder: Privacy Compared",
    "Google Photos Free Storage Policy Changes Explained: Impact on Existing Libraries":
        "Google Photos Free Storage Policy: What Changed for Your Library",
    "How to Transfer Samsung Health Data to a New Phone Without Losing Records":
        "How to Transfer Samsung Health Data to a New Phone Without Loss",
    "Fallout New Vegas vs. Fallout 3 Remaster: What We Know and What to Expect":
        "Fallout New Vegas vs. Fallout 3 Remaster: What We Know So Far",
    "Fallout New Vegas Endings Explained: How Player Choices Impact the Mojave":
        "Fallout New Vegas Endings Explained: How Your Choices Matter",
    "Fallout New Vegas Modding Guide: Essential Quality of Life and Content Mods":
        "Fallout New Vegas Modding Guide: Essential Quality-of-Life Mods",
    "Steam Deck Verified Games: What the Compatibility Ratings Actually Mean":
        "Steam Deck Verified: What the Compatibility Ratings Actually Mean",
    "Samsung Health Data Management: Backup, Export, and Health Connect Guide":
        "Samsung Health Data: Backup, Export, and Health Connect Guide",
    "Galaxy Z Fold 8 vs Fold 7 Camera: What Actually Changed and Why It Matters":
        "Galaxy Z Fold 8 vs Fold 7 Camera: What Actually Changed",
    "How Samsung's Silicon-Carbon Batteries Improve Galaxy Z Fold 8 Battery Life":
        "How Silicon-Carbon Batteries Improve Galaxy Z Fold 8 Battery Life",
    "Google Pixel Launcher vs Third-Party Android Launchers: Features and Customization":
        "Pixel Launcher vs Third-Party Android Launchers: Features Compared",
    "Galaxy Z Fold 7 vs Fold 8 Camera Comparison: Sensor, Zoom, and Low Light":
        "Galaxy Z Fold 7 vs Fold 8 Camera: Sensor, Zoom, and Low Light",
    "Google Assistant vs Gemini: What Changes When Assistant Shuts Down on September 4":
        "Google Assistant vs Gemini: What Changes When Assistant Goes Away",
    "Android 15/16 Native App Lock vs Samsung App Lock: Privacy Features Compared":
        "Android Native App Lock vs Samsung App Lock: Privacy Compared",
    "Samsung Galaxy Z Fold 8 Ultra vs Galaxy S26 Ultra: Camera Specs Compared":
        "Galaxy Z Fold 8 Ultra vs Galaxy S26 Ultra: Camera Specs Compared",
    "Nintendo Switch 2 MicroSD Express: Why Old Cards Don't Work and What Does":
        "Nintendo Switch 2 microSD Express: Why Old Cards Don't Work",
    "How to Customize Pixel Quick Settings with Android 17 QPR2 Beta Features":
        "How to Customize Pixel Quick Settings with Android 17 QPR2 Beta",
    "Pixel 11 Pro Fold vs Pixel 11 Pro: Camera and Display Features Comparison":
        "Pixel 11 Pro Fold vs Pixel 11 Pro: Camera and Display Compared",
    "How to Set Up and Expand Storage on Nintendo Switch 2 with microSD Express":
        "How to Expand Nintendo Switch 2 Storage with microSD Express",
    "Nvidia DLSS 5 Explained: How 3D-Guided Neural Rendering Improves Game Performance":
        "Nvidia DLSS 5 Explained: How 3D-Guided Neural Rendering Works",
    "Galaxy Z Fold 8 vs Galaxy Z Flip 8: Which foldable phone should you buy":
        "Galaxy Z Fold 8 vs Z Flip 8: Which Foldable Should You Buy?",
    "Steam Frame vs Steam Deck: performance, price, and portability compared":
        "Steam Frame vs Steam Deck: Performance, Price, and Portability",
}
# (참고) 'Google Messages Long-Press Menu Redesign...'(72자)는 Google 1위 페이지라서 일부러 바꾸지 않는다.

# ── 4) 금지 표현 교체 ──────────────────────────────────────────────────
PHRASES = [
    (r"\bcomprehensive\b", "complete"),
    (r"\brobust\b", "strong"),
    (r"\bcutting-edge\b", "latest"),
    (r"\bdelves into\b", "looks at"),
    (r"\bdelve into\b", "look at"),
    (r"\bhinges on\b", "depends on"),
    (r"\bunderscores\b", "highlights"),
    (r"\bunderscore\b", "highlight"),
    (r"\bunderscoring\b", "highlighting"),
    (r"\bvibrant\b", "rich"),
]

# ── 2) 링크 정리 ───────────────────────────────────────────────────────
BANNED = r"(?:wikipedia\.org|techradar\.com|gsmarena\.com|youtube\.com|youtu\.be|reddit\.com|gamerant\.com|fextralife|cnet\.com|phonearena\.com|tomsguide\.com|sammobile\.com|gadgets360\.com)"
NEWS = r"(?:androidauthority\.com|9to5google\.com|theverge\.com|arstechnica\.com|eurogamer\.net|pcgamer\.com|windowscentral\.com|engadget\.com|techcrunch\.com|tomshardware\.com|digitaltrends\.com|gizmodo\.com|wired\.com|androidpolice\.com|xda-developers\.com)"
URL = r"https?://[^\s()]*(?:\([^()\s]*\)[^\s()]*)*"        # 주소 속 괄호 허용 (예: Steam_Machine_(2026))
MDLINK = re.compile(r"\[([^\]]+)\]\((" + URL + r")\)")
BAD_URL = re.compile(r"^https?://(?:[^/]*\.)?" + BANNED + r"|^https?://(?:www\.)?" + NEWS + r"/?$", re.I)


def is_bad(url):
    if re.match(r"^https?://(?:[^/]*\.)?" + BANNED, url, re.I) and re.search(BANNED, url.split("/")[2], re.I):
        return True
    return bool(re.match(r"^https?://(?:www\.)?" + NEWS + r"/?$", url, re.I))


def split_fm(text):
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    return text[:end + 4], text[end + 4:]


def norm(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')).strip().lower()


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        v = v[1:-1].replace("''", "'")
    return v


def yq(s):
    return "'" + s.replace("'", "''") + "'"


def clean_text(t):
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"[*`#>]", "", t)
    return re.sub(r"\s+", " ", t).strip()


TRAIL = {"and", "or", "the", "a", "an", "of", "to", "in", "on", "for", "with", "by", "from", "as", "at",
         "that", "which", "is", "are", "was", "were", "when", "where", "how", "what", "why", "than", "then",
         "but", "if", "because", "while", "into", "about", "your", "you", "it", "its", "this", "also"}


def cut_clause(text, limit):
    if len(text) <= limit:
        return text
    head = text[:limit]
    best = max(head.rfind(", "), head.rfind(" — "), head.rfind(" - "), head.rfind("; "))
    out = head[:best] if best >= max(25, int(len(head) * 0.5)) else head.rsplit(" ", 1)[0]
    words = out.split()
    while words and words[-1].lower().strip(",.;:") in TRAIL:
        words.pop()
    return " ".join(words).rstrip(" ,;:-—") + "."


def trim_excerpt(ex, limit=150):
    sents = re.split(r"(?<=[.!?])\s+", clean_text(ex))
    out, used = "", 0
    for s in sents:
        cand = (out + " " + s).strip()
        if len(cand) <= limit:
            out, used = cand, used + 1
        else:
            break
    if len(out) < 100 and used < len(sents):
        room = limit - len(out) - 1
        if room >= 35:
            part = cut_clause(sents[used], room)
            if len(part) >= 30:
                out = (out + " " + part).strip()
    return out if len(out) >= 60 else cut_clause(clean_text(ex), limit)


def process_post(path, stats):
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    fm, body = split_fm(raw)
    if not fm:
        return None
    new_fm, new_body = fm, body
    notes = []

    # 1) 제목 단축
    m = re.search(r"^title:[ \t]*(.*?)(\r?)$", new_fm, re.M)
    if m:
        cur = unquote(m.group(1))
        key = norm(cur)
        for old, new in TITLES.items():
            if norm(old) == key:
                new_fm = new_fm[:m.start()] + "title: " + yq(new) + m.group(2) + new_fm[m.end():]
                notes.append(f"제목 {len(cur)}자→{len(new)}자: {new}")
                stats["titles"] += 1
                break

    # 5) excerpt 정리 (156자 초과)
    m = re.search(r"^excerpt:[ \t]*(.*?)(\r?)$", new_fm, re.M)
    if m and not m.group(1).startswith((">", "|")):
        cur = unquote(m.group(1))
        if len(cur) > 156:
            new = trim_excerpt(cur)
            if new and new != cur:
                new_fm = new_fm[:m.start()] + "excerpt: " + yq(new) + m.group(2) + new_fm[m.end():]
                notes.append(f"excerpt {len(cur)}자→{len(new)}자: {new}")
                stats["excerpts"] += 1

    # 2) 금지 출처 / 루트 링크
    removed_src, unlinked = 0, 0
    lines = new_body.split("\n")
    kept = []
    for line in lines:
        links = MDLINK.findall(line)
        if links and re.match(r"^\s*(?:[-*]|\d+\.)\s+(?:\[\d+\]\s*)?\[", line) and all(is_bad(u) for _, u in links[:1]):
            removed_src += 1            # Sources 목록 한 줄이 통째로 금지 출처
            continue
        kept.append(line)
    new_body = "\n".join(kept)

    def unlink(mm):
        nonlocal unlinked
        if is_bad(mm.group(2)):
            unlinked += 1
            return mm.group(1)
        return mm.group(0)
    new_body = MDLINK.sub(unlink, new_body)
    if removed_src or unlinked:
        notes.append(f"출처 정리: Sources 줄 {removed_src}개 삭제, 본문 링크 {unlinked}개 해제")
        stats["links"] += removed_src + unlinked
        # 목록이 비어 버린 "Sources:" 제목 정리
        new_body = re.sub(r"\n(?:\*\*)?Sources:?(?:\*\*)?[ \t]*\n(?:\s*\n)*(?=\s*$|\n---|\n\*\*Want)", "\n", new_body)

    # 1) 깨진 허브 링크
    if "samsung-health-data-ecosystem_hub" in new_body:
        new_body = new_body.replace("samsung-health-data-ecosystem_hub/", "samsung-health-data-ecosystem/")
        notes.append("깨진 허브 링크(_hub) 수정")
        stats["hub"] += 1
        # 같은 푸터가 연달아 두 번이면 하나만
        pat = re.compile(r"(\n---\n\*\*Want the full picture\?\*\*[^\n]*\n)(?:\s*\n)*(?:---\n\*\*Want the full picture\?\*\*[^\n]*\n)+")
        new_body = pat.sub(r"\1", new_body)

    # 4) 금지 표현 (제목 줄과 링크 주소는 건드리지 않음)
    swaps = 0

    def repl_text(t):
        nonlocal swaps
        for pat, rep in PHRASES:
            def r(mm, rep=rep):
                nonlocal swaps
                swaps += 1
                w = mm.group(0)
                return rep.capitalize() if w[:1].isupper() else rep
            t = re.sub(pat, r, t, flags=re.I)
        return t
    parts = re.split(r"(\]\([^)]*\)|https?://\S+)", new_body)      # 링크 주소는 건너뜀
    new_body = "".join(p if i % 2 else repl_text(p) for i, p in enumerate(parts))
    if swaps:
        notes.append(f"금지 표현 {swaps}곳 교체")
        stats["phrases"] += swaps

    if new_fm + new_body != raw:
        return notes, new_fm + new_body
    return None


def process_pages(stats):
    DESC = {
        "about": "Frontbuffer is an independent tech and gaming site publishing practical guides, fixes, and comparisons.",
        "disclosure": "How Frontbuffer researches, writes, and funds its articles, including how we use AI tools.",
        "privacy": "How Frontbuffer handles visitor data, including analytics, cookies, and third-party services.",
    }
    if not PAGES.is_dir():
        return
    for p in sorted(PAGES.glob("*.md")):
        key = next((k for k in DESC if k in p.name.lower()), None)
        if not key:
            continue
        with open(p, encoding="utf-8", newline="") as fh:
            raw = fh.read()
        fm, body = split_fm(raw)
        if not fm or re.search(r"^description:", fm, re.M):
            continue
        new = fm.replace("\n---", f"\ndescription: {yq(DESC[key])}\n---", 1) if fm.endswith("\n---") else fm
        print(f"\n{'적용' if APPLY else '대상'}: _pages/{p.name}\n   + description: {DESC[key]}")
        stats["pages"] += 1
        if APPLY and new != fm:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(new + body)


def main():
    stats = {"titles": 0, "excerpts": 0, "links": 0, "hub": 0, "phrases": 0, "pages": 0}
    dates, touched = [], 0
    for p in sorted(POSTS.glob("*.md")):
        res = process_post(p, stats)
        if not res:
            continue
        notes, new = res
        touched += 1
        print(f"\n{'적용' if APPLY else '대상'}: {p.name}")
        for n in notes:
            print("   ·", n)
        if any(n.startswith(("제목", "excerpt")) for n in notes):
            d = re.match(r"^(\d{4}-\d{2}-\d{2})", p.name).group(1)
            if d not in dates:
                dates.append(d)
        if APPLY:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
    process_pages(stats)
    print("\n" + "=" * 60)
    print(f"{'적용' if APPLY else '대상'} 글 {touched}개 | 제목 {stats['titles']} · excerpt {stats['excerpts']} · "
          f"링크/출처 {stats['links']} · 허브 링크 {stats['hub']} · 금지 표현 {stats['phrases']} · 페이지 설명 {stats['pages']}")
    if dates:
        print("\nOG 재생성 날짜 (Actions → OG Image Regenerate → date 칸):")
        print(" ".join(sorted(dates)))
    if not APPLY:
        print("\n결과가 괜찮으면: python fix_site_issues.py --apply")


if __name__ == "__main__":
    main()
