# =====================================================================
# 🔧 published/ 아카이브 복구 (fix_archive.py) — 1회 실행용
# =====================================================================
# 배경: publish_one.py와 record_publish()가 둘 다 published/에 쓰면서
#       2026-07-21 아카이브가 판정 리포트 내용으로 덮어써짐.
#       (git log: review_report_*.txt => published/*.md rename 확인)
#
# 조치: _posts/의 정상 파일을 published/로 다시 복사.
#       _posts/는 Jekyll이 실제 발행에 쓰는 파일이라 내용이 정확함.
#
# 사용법: python fix_archive.py
# 실행 후 이 파일은 삭제해도 됨.
# =====================================================================

import os
import shutil
from pathlib import Path

POSTS_DIR     = "_posts"
PUBLISHED_DIR = "research_data/write/published"


def main():
    if not os.path.isdir(POSTS_DIR):
        print(f"❌ {POSTS_DIR} 없음")
        return

    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    fixed   = []
    skipped = []

    for post in sorted(Path(POSTS_DIR).glob("*.md")):
        archive = Path(PUBLISHED_DIR) / post.name

        if not archive.exists():
            shutil.copy2(post, archive)
            fixed.append(f"{post.name} (신규 생성)")
            continue

        post_text    = post.read_text(encoding="utf-8", errors="replace")
        archive_text = archive.read_text(encoding="utf-8", errors="replace")

        # front matter가 없으면 손상된 아카이브 (판정 리포트 등)
        if not archive_text.lstrip().startswith("---"):
            shutil.copy2(post, archive)
            fixed.append(f"{post.name} (손상 복구 — front matter 없음)")
        elif post_text != archive_text:
            shutil.copy2(post, archive)
            fixed.append(f"{post.name} (내용 불일치 복구)")
        else:
            skipped.append(post.name)

    print()
    if fixed:
        print(f"✅ 복구 완료 ({len(fixed)}건):")
        for f in fixed:
            print(f"   • {f}")
    if skipped:
        print(f"\nℹ️  정상 (변경 없음): {len(skipped)}건")

    if fixed:
        print()
        print("다음 명령으로 커밋하세요:")
        print("  git add research_data/write/published/")
        print('  git commit -m "fix: published 아카이브 복구 (중복 아카이브 버그)"')
        print("  git push origin master:main")
    else:
        print("\n✅ 복구할 것 없음")


if __name__ == "__main__":
    main()
