#!/usr/bin/env python3
# =====================================================================
# 🧹 published/ 보관 폴더의 고아 파일 정리 (clean_published_orphans.py)
# =====================================================================
# research_data/write/published/ 는 발행한 글의 보관 사본이다.
# 중복 정리로 _posts/ 에서 삭제한 글의 사본이 남아 있으면 Step 5 가 매주
# "_posts/에 없음 (발행 누락?)" 으로 수동 확인 항목에 올린다 (현재 18건).
# 이 스크립트는 그런 사본을 삭제하지 않고 research_data/write/published_removed/ 로 옮긴다.
#
# 사용법 (저장소 루트에서):
#   python clean_published_orphans.py            ← 미리보기
#   python clean_published_orphans.py --apply    ← 이동
# =====================================================================

import shutil
import sys
from pathlib import Path

POSTS = Path("_posts")
PUB = Path("research_data/write/published")
DEST = Path("research_data/write/published_removed")
APPLY = "--apply" in sys.argv


def main():
    if not PUB.is_dir():
        print("published/ 폴더가 없습니다")
        return
    post_names = {p.name for p in POSTS.glob("*.md")}
    orphans = sorted(p for p in PUB.glob("*.md") if p.name not in post_names)
    print(f"published/ {len(list(PUB.glob('*.md')))}개 중 _posts/ 에 없는 파일 {len(orphans)}개")
    for p in orphans:
        print(f"  {'이동' if APPLY else '대상'}: {p.name}")
    if APPLY and orphans:
        DEST.mkdir(parents=True, exist_ok=True)
        for p in orphans:
            shutil.move(str(p), str(DEST / p.name))
        print(f"\n✅ {len(orphans)}개를 {DEST} 로 옮겼습니다")
    elif orphans:
        print("\n적용하려면: python clean_published_orphans.py --apply")


if __name__ == "__main__":
    main()
