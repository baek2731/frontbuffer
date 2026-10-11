#!/usr/bin/env python3
# =====================================================================
# 🩹 fix_site_issues.py 적용 후 후속 보정 (fix_followups.py)
# =====================================================================
# 1. Steam Machine LED 글(07-15): 금지 출처(TechRadar·Wikipedia)를 걷어낸 자리에 남은 문장 2곳을
#    확인된 출처(TweakTown, Club386)로 바로잡고, 틀린 하드웨어 설명(메모리 슬롯)을 고친다.
#      - "TechRadar's coverage of Valve's official fix" → Valve 지원 계정 안내 + TweakTown 링크
#      - "single SO-DIMM ... rather than dual memory slots" → 슬롯은 2개이고 기본 1개만 장착
#        (Steam Machine 은 SO-DIMM 슬롯이 2개, 출하 시 16GB 한 개만 들어 있음)
# 2. 자동 교체 후 어색해진 표현 정리 (a advanced → an advanced, more strong → stronger 등)
# 3. Fallout explainer excerpt 문장 끊김 수정, AYANEO 문장 보정
# 4. 같은 "Want the full picture?" 푸터가 두 번 이상이면 하나만 남김
#
# 사용법 (저장소 루트에서):
#   python fix_followups.py            ← 미리보기
#   python fix_followups.py --apply    ← 적용
# =====================================================================

import re
import sys
from pathlib import Path

POSTS = Path("_posts")
APPLY = "--apply" in sys.argv

TWEAK_FIX = "https://tweaktown.com/news/112530/the-dreaded-steam-machine-red-line-of-death-was-fixed-after-a-simple-cmos-reset/index.html"
TWEAK_RAM = "https://tweaktown.com/news/112406/steam-machine-loses-up-to-20-percent-of-its-performance-with-its-out-of-the-box-single-16gb-ddr5-so-dimm/index.html"
CLUB386 = "https://www.club386.com/?p=148778"

# 파일명 패턴 → [(찾을 문장, 바꿀 문장)]
EDITS = {
    "steam-machine-led-error-codes": [
        ("These steps follow TechRadar's coverage of Valve's official fix.",
         f"These steps follow the recovery procedure Valve's hardware support account posted on Reddit, as reported by [TweakTown]({TWEAK_FIX})."),
        ("the system uses a **single SO-DIMM DDR5 memory stick** (16GB) rather than dual memory slots, and **one M.2 NVMe SSD slot** supporting both 2230 and 2280 form factors, per the Steam Machine (2026) specification page.",
         f"the system ships with a **single 16GB DDR5-5600 SO-DIMM** and has a second SO-DIMM slot you can fill yourself ([TweakTown]({TWEAK_RAM})), plus **one M.2 NVMe SSD slot** that holds the stock 2230 drive and also fits 2260 and 2280 drives ([Club386]({CLUB386}))."),
    ],
    "2026-07-24-fallout-series_explainer": [],
}
EXCERPTS = {
    "fallout-series_explainer":
        "Fallout: New Vegas has four main endings — NCR, Legion, Mr. House, and Independent — and which one you get depends on late-game choices.",
}
SOURCES_ADD = {
    "steam-machine-led-error-codes": [
        f"* [TweakTown — Steam Machine \"Red Line of Death\" was fixed after a simple CMOS reset]({TWEAK_FIX})",
        f"* [TweakTown — Steam Machine ships with a single 16GB DDR5 SO-DIMM]({TWEAK_RAM})",
        f"* [Club386 — Steam Machine review]({CLUB386})",
    ],
}
GLOBAL = [
    ("a advanced foldable form factor", "an advanced foldable form factor"),
    ("how Google is advancing of mobile technology", "how Google is advancing mobile technology"),
    ("even more strong and user-friendly", "even stronger and more user-friendly"),
    ("with latest AMD hardware", "with the latest AMD hardware"),
]
FOOTER = re.compile(r"^\*\*Want the full picture\?\*\*.*$", re.M)


def yq(s):
    return "'" + s.replace("'", "''") + "'"


def dedupe_footers(body):
    lines = body.split("\n")
    seen, out, i = set(), [], 0
    # 같은 푸터 줄이 다시 나오면, 앞의 '---' 구분선과 빈 줄까지 함께 제거
    for idx, line in enumerate(lines):
        if FOOTER.match(line):
            if line in seen:
                while out and out[-1].strip() == "":
                    out.pop()
                if out and out[-1].strip() == "---":
                    out.pop()
                continue
            seen.add(line)
        out.append(line)
    return "\n".join(out)


def main():
    changed = 0
    for p in sorted(POSTS.glob("*.md")):
        with open(p, encoding="utf-8", newline="") as fh:
            raw = fh.read()
        text, notes = raw, []

        for key, pairs in EDITS.items():
            if key in p.name:
                for old, new in pairs:
                    if old in text:
                        text = text.replace(old, new, 1)
                        notes.append("문장 교체: " + old[:60] + "...")
                    elif new not in text:
                        notes.append("⚠️ 찾지 못함(이미 수정됐거나 문장이 다름): " + old[:60] + "...")
        for key, lines in SOURCES_ADD.items():
            if key in p.name and lines[0] not in text:
                m = list(re.finditer(r"^\* \[.*\]\(.*\)[ \t]*$", text, re.M))
                if m:
                    last = m[-1]
                    text = text[:last.end()] + "\n" + "\n".join(lines) + text[last.end():]
                    notes.append(f"Sources 에 출처 {len(lines)}개 추가")
                else:
                    notes.append("⚠️ Sources 목록을 찾지 못해 출처를 추가하지 못함 — 직접 추가 필요")
        for key, ex in EXCERPTS.items():
            if key in p.name:
                m = re.search(r"^excerpt:[ \t]*(.*?)(\r?)$", text, re.M)
                if m and ex not in m.group(1):
                    text = text[:m.start()] + "excerpt: " + yq(ex) + m.group(2) + text[m.end():]
                    notes.append("excerpt 교체")
        for old, new in GLOBAL:
            if old in text:
                text = text.replace(old, new)
                notes.append(f"표현 보정: {old} → {new}")
        before = text
        text = dedupe_footers(text)
        if text != before:
            notes.append("중복 푸터 제거")

        if text != raw:
            changed += 1
            print(f"\n{'적용' if APPLY else '대상'}: {p.name}")
            for n in notes:
                print("   ·", n)
            if APPLY:
                with open(p, "w", encoding="utf-8", newline="") as fh:
                    fh.write(text)
        elif notes:
            print(f"\n확인: {p.name}")
            for n in notes:
                print("   ·", n)
    print(f"\n{'적용' if APPLY else '대상'} 글 {changed}개")
    if not APPLY and changed:
        print("결과가 괜찮으면: python fix_followups.py --apply")
    print("\nOG 재생성이 필요한 날짜(excerpt 변경): 2026-07-24")


if __name__ == "__main__":
    main()
