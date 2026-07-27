"""
W30 content_pipeline.json 중복 클러스터 정리 스크립트.

같은 hub_keyword/folder를 공유하는 중복 클러스터 중
Grade A 기준으로 가장 대표성 있는 것 하나만 남기고
나머지는 status → "rejected"로 변경.

남길 것 (Grade A, 독립적):
  - Samsung Galaxy Z Fold 8          (folder: 01-galaxy-fold, RISING 1.47, current 98)
  - Samsung Galaxy Fold Flip Series  (folder: 01-galaxy-fold, 키워드 4개)
  - Google Android Ecosystem         (folder: 05-android-auto, 월 5000, LOW경쟁)

rejected로 변경:
  - Samsung Galaxy Foldables                      (04-samsung-galaxy, 중복)
  - Samsung Galaxy Foldable Phones & Wearables   (04-samsung-galaxy, 중복)
  - Samsung Foldable Phones                       (04-samsung-galaxy, 중복)
  - Samsung Galaxy & Google Pixel Phones          (04-samsung-galaxy, 중복)
  - Google Android Features                       (05-android-auto, Grade B, 품질 미달)

실행:
  python fix_w30_pipeline.py content_pipeline.json
"""

import json
import sys
from datetime import datetime, timezone

PIPELINE_FILE = sys.argv[1] if len(sys.argv) > 1 else "content_pipeline.json"
WEEK = "2026-W30"

REJECT_CLUSTERS = {
    "Samsung Galaxy Foldables",
    "Samsung Galaxy Foldable Phones & Wearables",
    "Samsung Foldable Phones",
    "Samsung Galaxy & Google Pixel Phones",
    "Google Android Features",
    # Grade C 전부도 정리 (이미 write.py가 막지만 명시적으로)
    "Gaming Platform Choices",
    "Google AI Features",
    "PC Gaming Optimization",
    "Google Gemini for Home",
    "Xbox PC App Issues",
    "PC Gaming Ecosystem",
    "Google Pixel Ecosystem",
    "Gaming Ecosystem Strategy",
    "AI Models and Services",
}

with open(PIPELINE_FILE, encoding="utf-8") as f:
    data = json.load(f)

week_sels = data.get("weekly_selections", {}).get(WEEK, [])
changed = 0

for sel in week_sels:
    name = sel.get("cluster_name", "")
    if name in REJECT_CLUSTERS and sel.get("status") != "rejected":
        sel["status"] = "rejected"
        changed += 1
        print(f"  ❌ rejected: {name}")
    elif sel.get("status") == "candidate":
        print(f"  ✅ 유지:     {name} [{sel.get('data_grade','?')}]")

data["_last_updated"] = datetime.now(timezone.utc).isoformat()

with open(PIPELINE_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n총 {changed}개 클러스터 rejected 처리 완료.")
print(f"남은 candidate: {sum(1 for s in week_sels if s.get('status') == 'candidate')}개")
