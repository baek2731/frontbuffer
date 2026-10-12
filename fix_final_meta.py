#!/usr/bin/env python3
# =====================================================================
# 🏁 마지막 meta 정리 (fix_final_meta.py)
# =====================================================================
# site_check.py 에 남은 지적(meta description 짧음, og:image 없음)을 처리한다.
#   1. excerpt 가 110자 미만이 된 글 2개를 120~150자로 다시 쓴다
#        - 08-31 Switch 2 microSD Express / 08-05 실리콘카본 배터리
#   2. About / Disclosure / Privacy 페이지의 description 을 115~150자로 늘리고
#      header.og_image(기본 OG 이미지)를 지정한다
#      (assets/images/og-default.png 가 없으면 og_image 는 건너뛴다)
#
# 사용법 (저장소 루트에서):
#   python fix_final_meta.py            ← 미리보기
#   python fix_final_meta.py --apply    ← 적용
# =====================================================================

import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
POSTS = Path("_posts")
PAGES = Path("_pages")
OG_FILE = Path("assets/images/og-default.png")
OG_PATH = "/assets/images/og-default.png"

EXCERPTS = {
    "rumored-nintendo-switch-successor":
        "Nintendo Switch 2 needs microSD Express cards, and your old Switch 1 card won't store games. See which cards work and how much space you need.",
    "samsung-galaxy-z-foldflip-series_explainer":
        "Silicon-carbon cells let the Galaxy Z Fold 8 Ultra fit a 5,000mAh battery where the Fold 7 had 4,400mAh. Here is how they work and what changes.",
}
DESC = {
    "about": "Frontbuffer is an independent tech and gaming site. We publish practical guides, fixes, and comparisons for Android, Pixel, Galaxy, and Steam.",
    "disclosure": "How Frontbuffer researches and writes its articles, how the site is funded, and how we use AI tools in that process.",
    "privacy": "How Frontbuffer collects and uses visitor data, including analytics and cookies, and what choices you have over that data.",
}


def yq(s):
    return "'" + s.replace("'", "''") + "'"


def read(p):
    with open(p, encoding="utf-8", newline="") as fh:
        return fh.read()


def write(p, t):
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)


def split_fm(text):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    return text[:end], text[end:]          # fm(마지막 --- 제외), 나머지('\n---' 이후)


def main():
    changed = 0
    for p in sorted(POSTS.glob("*.md")):
        for key, ex in EXCERPTS.items():
            if key in p.name:
                text = read(p)
                m = re.search(r"^excerpt:[ \t]*(.*?)(\r?)$", text, re.M)
                if m and yq(ex) != m.group(1).strip():
                    print(f"{'적용' if APPLY else '대상'}: {p.name}\n   excerpt ({len(ex)}자): {ex}")
                    changed += 1
                    if APPLY:
                        write(p, text[:m.start()] + "excerpt: " + yq(ex) + m.group(2) + text[m.end():])

    if not OG_FILE.exists():
        print(f"\n⚠️ {OG_FILE} 가 없어서 og_image 지정은 건너뜁니다 (파일을 먼저 넣으세요)")
    for p in sorted(PAGES.glob("*.md")) if PAGES.is_dir() else []:
        key = next((k for k in DESC if k in p.name.lower()), None)
        if not key:
            continue
        text = read(p)
        fm, rest = split_fm(text)
        if fm is None:
            continue
        nl = "\r\n" if "\r\n" in fm else "\n"
        new_fm = fm
        if re.search(r"^description:", new_fm, re.M):
            new_fm = re.sub(r"^description:.*$", "description: " + yq(DESC[key]), new_fm, count=1, flags=re.M)
        else:
            new_fm += nl + "description: " + yq(DESC[key])
        notes = [f"description ({len(DESC[key])}자)"]
        if OG_FILE.exists() and not re.search(r"^header:", new_fm, re.M):
            new_fm += nl + "header:" + nl + "  og_image: " + OG_PATH
            notes.append("header.og_image 지정")
        elif OG_FILE.exists() and re.search(r"^header:", new_fm, re.M) and "og_image" not in new_fm:
            new_fm = re.sub(r"^(header:[ \t]*\r?\n)", lambda mm: mm.group(1) + "  og_image: " + OG_PATH + nl, new_fm, count=1, flags=re.M)
            notes.append("기존 header 아래에 og_image 추가")
        if new_fm != fm:
            print(f"{'적용' if APPLY else '대상'}: _pages/{p.name}\n   " + ", ".join(notes))
            changed += 1
            if APPLY:
                write(p, new_fm + rest)
    print(f"\n{'적용' if APPLY else '대상'} {changed}건")
    print("OG 재생성이 필요한 날짜(excerpt 변경): 2026-08-31 2026-08-05")
    if not APPLY and changed:
        print("\n결과가 괜찮으면: python fix_final_meta.py --apply")


if __name__ == "__main__":
    main()
