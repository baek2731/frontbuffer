"""
final/의 기존 HUB 파일 016_, 017_ → H001_, H002_ 로 변경
"""
from pathlib import Path

FINAL_DIR = Path("research_data/write/final")

hub_files = sorted([
    f for f in FINAL_DIR.glob("*.md")
    if f.name.endswith("_HUB.md") and not f.name.startswith("H")
    and not f.name.startswith("review_report_")
])

for i, f in enumerate(hub_files, 1):
    # 016_2026-W30_samsung-health-data-ecosystem_HUB.md
    # → H001_2026-W30_samsung-health-data-ecosystem_HUB.md
    parts = f.name.split("_", 1)
    new_name = f"H{i:03d}_{parts[1]}"
    new_f = FINAL_DIR / new_name
    f.rename(new_f)
    print(f"✅ {f.name} → {new_name}")

    # review_report도 변경
    old_stem = f.stem
    new_stem = new_f.stem
    review = FINAL_DIR / f"review_report_{old_stem}.txt"
    if review.exists():
        review.rename(FINAL_DIR / f"review_report_{new_stem}.txt")
        print(f"   review_report 변경 완료")

print("\n완료")
