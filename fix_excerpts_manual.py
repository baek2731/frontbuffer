#!/usr/bin/env python3
# =====================================================================
# ✍️ excerpt 수동 보정 (fix_excerpts_manual.py)
# =====================================================================
# fix_excerpts.py 로 자동 정리한 뒤에도 문장 끝이 어색한 글 10개를
# 직접 쓴 문장으로 교체한다. 해당 글의 excerpt 줄만 바뀐다.
#
# 사용법 (저장소 루트에서):
#   python fix_excerpts_manual.py           ← 미리보기
#   python fix_excerpts_manual.py --apply   ← 적용
# =====================================================================

import re
import sys
from pathlib import Path

POSTS = Path("_posts")

FIXES = {
    "2026-07-22-android-ecosystem_guide.md":
        "Samsung Health data transfers automatically via Samsung Cloud, but only if sync was enabled before you switched. Here is how to move it to a new phone.",
    "2026-07-31-portable-gaming_guide.md":
        "Sunshine runs on your PC as the host and Moonlight runs on your Android tablet as the client. Here is how to set up and pair them.",
    "2026-08-04-samsung-galaxy-z-foldflip-series_comparison.md":
        "Samsung announced the Galaxy Z Fold 8 and Fold 8 Ultra on July 22, 2026, and both ship August 7. Here is how the two models differ.",
    "2026-08-19-google-assistant-vs-gemini-what-changes-when-assistant-shuts.md":
        "Google confirmed Assistant will be removed from Android phones, tablets, Wear OS watches, and more. Here is what changes when Gemini takes over.",
    "2026-08-20-what-is-vram-and-how-much-do-you-need-for-pc-gaming-in-2026.md":
        "Games like Alan Wake 2 and Cyberpunk 2077: Phantom Liberty showed that VRAM can limit performance even at 1080p. Here is how much you need.",
    "2026-08-27-android-desktop-mode-vs-samsung-dex-a-comprehensive-comparis.md":
        "Samsung introduced DeX with the Galaxy S8 in 2017. Here is how Android's native desktop mode compares with DeX today.",
    "2026-08-28-android-1516-native-app-lock-vs-samsung-app-lock-privacy-fea.md":
        "Android now includes a native app lock at the system level. Here is how it compares with Samsung's App Lock on privacy and features.",
    "2026-09-13-galaxy-z-fold-8-vs-fold-7-hinge-durability-comparison.md":
        "The Galaxy Z Fold 8 replaced the Fold 7's Armor FlexHinge with a dual-rail hinge. Here is what that means for durability.",
    "2026-09-18-04-pixel-pro.md":
        "The Pixel 11 Pro ships with Android 17 and Tensor G6. Here is what to set up first, including Video Boost, Pro Controls, and Night Sight Video.",
    "2026-09-25-steam-frame-vs-steam-deck-performance-price-and-portability-.md":
        "Valve now has two portable devices: the Steam Deck handheld and the Steam Frame VR headset. Both run SteamOS but serve very different uses.",
}


def main():
    apply = "--apply" in sys.argv
    done = 0
    for name, new in FIXES.items():
        p = POSTS / name
        if not p.exists():
            print(f"없음(건너뜀): {name}")
            continue
        if len(new) > 155:
            print(f"⚠️ 155자 초과({len(new)}): {name}")
        with open(p, encoding="utf-8", newline="") as fh:
            text = fh.read()
        m = re.search(r"^excerpt:[ \t]*(.*?)(\r?)$", text, re.M)
        if not m:
            print(f"excerpt 줄 없음(건너뜀): {name}")
            continue
        val = "'" + new.replace("'", "''") + "'"
        print(f"{'적용' if apply else '대상'}: {name}")
        print(f"   → ({len(new)}자) {new}")
        done += 1
        if apply:
            text = text[:m.start()] + "excerpt: " + val + m.group(2) + text[m.end():]
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
    print(f"\n{'적용' if apply else '대상'}: {done}개")
    if not apply:
        print("적용하려면: python fix_excerpts_manual.py --apply")


if __name__ == "__main__":
    main()
