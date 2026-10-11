#!/usr/bin/env python3
# =====================================================================
# 📎 Steam Machine LED 글(07-15)에 출처 3개 추가 (fix_led_sources.py)
# =====================================================================
# fix_followups.py 가 Sources 목록을 못 찾아서 건너뛴 부분만 처리한다.
#   - "Sources:" 제목이 있으면 그 바로 아래에 3줄 추가
#   - 제목이 없으면 글 맨 끝에 Sources 블록을 새로 만든다
#
# 사용법 (저장소 루트에서):
#   python fix_led_sources.py            ← 미리보기 (글 끝부분 출력)
#   python fix_led_sources.py --apply    ← 적용
# =====================================================================

import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
LINES = [
    '* [TweakTown — Steam Machine "Red Line of Death" was fixed after a simple CMOS reset](https://tweaktown.com/news/112530/the-dreaded-steam-machine-red-line-of-death-was-fixed-after-a-simple-cmos-reset/index.html)',
    '* [TweakTown — Steam Machine ships with a single 16GB DDR5 SO-DIMM](https://tweaktown.com/news/112406/steam-machine-loses-up-to-20-percent-of-its-performance-with-its-out-of-the-box-single-16gb-ddr5-so-dimm/index.html)',
    '* [Club386 — Steam Machine review](https://www.club386.com/?p=148778)',
]


def main():
    files = sorted(Path("_posts").glob("*steam-machine-led-error-codes*.md"))
    if not files:
        print("❌ _posts 에서 Steam Machine LED 글을 찾지 못했습니다")
        return
    p = files[0]
    with open(p, encoding="utf-8", newline="") as fh:
        text = fh.read()
    nl = "\r\n" if "\r\n" in text else "\n"
    # 본문 속 인라인 링크와 구분하기 위해 "Sources 목록 줄" 자체가 있는지 확인한다
    body = text.replace("\r\n", "\n")
    missing = [l for l in LINES if l not in body]
    if not missing:
        print("ℹ️  Sources 목록에 이미 3줄이 들어 있습니다 — 할 일 없음")
        return
    m = re.search(r"^(?:\*\*)?Sources:?(?:\*\*)?[ \t]*$", body, re.M)
    if m:
        end = m.end()
        # 제목 다음의 빈 줄 하나를 건너뛴 위치에 삽입
        rest = body[end:]
        skip = re.match(r"\n[ \t]*\n", rest)
        pos = end + (skip.end() if skip else 1)
        new = body[:pos] + "\n".join(missing) + "\n" + body[pos:]
        how = f"Sources: 제목 아래에 {len(missing)}줄 추가"
    else:
        new = body.rstrip("\n") + "\n\n---\n\nSources:\n\n" + "\n".join(missing) + "\n"
        how = "Sources 블록을 글 끝에 새로 추가"
    print(f"{'적용' if APPLY else '대상'}: {p.name}\n   · {how}\n\n[결과 — 글 끝부분]")
    print("\n".join(new.split("\n")[-14:]))
    if APPLY:
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(new.replace("\n", nl))
        print("\n✅ 적용 완료")
    else:
        print("\n적용하려면: python fix_led_sources.py --apply")


if __name__ == "__main__":
    main()
