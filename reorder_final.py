"""
final/ 파일 넘버링 재정립 + content_pipeline.json publish_order 업데이트
review_report 미발행분 정리
"""
import json, datetime
from pathlib import Path

FINAL_DIR     = Path("research_data/write/final")
PIPELINE_FILE = "content_pipeline.json"
W30 = "2026-W30"
W29 = "2026-W29"

# ── 새 발행 순서 정의 ─────────────────────────────────────────────
# (새번호, 현재파일stem, cluster_name, content_type, week_tag, 새slug)
ORDER = [
    (1,  "portable-gaming_EXPLAINER",                               "Portable Gaming",                   "EXPLAINER",  W29, "portable-gaming"),
    (2,  "portable-gaming_GUIDE",                                   "Portable Gaming",                   "GUIDE",      W29, "portable-gaming"),
    (3,  "001_2026-W30_01-galaxy-fold_COMPARISON",                  "Samsung Galaxy Fold 8 Features",    "COMPARISON", W30, "01-galaxy-fold"),
    (4,  "004_2026-W30_01-galaxy-fold_EXPLAINER",                   "Samsung Galaxy Fold 8 Features",    "EXPLAINER",  W30, "01-galaxy-fold"),
    (5,  "005_2026-W30_01-galaxy-fold_GUIDE",                       "Samsung Galaxy Fold 8 Features",    "GUIDE",      W30, "01-galaxy-fold"),
    (6,  "999_2026-W30_samsung-galaxy-z-foldflip-series_COMPARISON","Samsung Galaxy Z Fold/Flip Series", "COMPARISON", W30, "samsung-galaxy-z-foldflip-series"),
    (7,  "999_2026-W30_samsung-galaxy-z-foldflip-series_EXPLAINER", "Samsung Galaxy Z Fold/Flip Series", "EXPLAINER",  W30, "samsung-galaxy-z-foldflip-series"),
    (8,  "999_2026-W30_samsung-galaxy-z-foldflip-series_GUIDE",     "Samsung Galaxy Z Fold/Flip Series", "GUIDE",      W30, "samsung-galaxy-z-foldflip-series"),
    (9,  "002_2026-W30_06-android-auto_COMPARISON",                 "Android Auto Troubleshooting",      "COMPARISON", W30, "06-android-auto"),
    (10, "006_2026-W30_06-android-auto_GUIDE",                      "Android Auto Troubleshooting",      "GUIDE",      W30, "06-android-auto"),
    (11, "999_2026-W30_google-android-ecosystem_COMPARISON",        "Google Android Ecosystem",          "COMPARISON", W30, "google-android-ecosystem"),
    (12, "999_2026-W30_google-android-ecosystem_EXPLAINER",         "Google Android Ecosystem",          "EXPLAINER",  W30, "google-android-ecosystem"),
    (13, "999_2026-W30_google-android-ecosystem_GUIDE",             "Google Android Ecosystem",          "GUIDE",      W30, "google-android-ecosystem"),
    (14, "003_2026-W30_gaming-media-formats_COMPARISON",            "Gaming Media Formats",              "COMPARISON", W30, "gaming-media-formats"),
    (15, "007_2026-W30_gaming-media-formats_GUIDE",                 "Gaming Media Formats",              "GUIDE",      W30, "gaming-media-formats"),
    (16, "999_2026-W30_samsung-health-data-ecosystem_HUB",          "Samsung Health Data Ecosystem",     "HUB",        W30, "samsung-health-data-ecosystem"),
    (17, "999_2026-W30_steam-machine-hardware-management_HUB",      "Steam Machine Hardware Management", "HUB",        W30, "steam-machine-hardware-management"),
]

# ── 1. final/ 파일명 변경 ─────────────────────────────────────────
print("=== final/ 파일명 변경 ===")
rename_map = {}  # old_stem → new_stem

for new_num, old_stem, cluster, ct, week, slug in ORDER:
    old_md  = FINAL_DIR / f"{old_stem}.md"
    new_stem = f"{new_num:03d}_{week}_{slug}_{ct}"
    new_md  = FINAL_DIR / f"{new_stem}.md"

    if old_md.exists():
        old_md.rename(new_md)
        rename_map[old_stem] = new_stem
        print(f"  ✅ {old_md.name}")
        print(f"     → {new_md.name}")
    else:
        print(f"  ⚠️  없음: {old_md.name}")

# ── 2. review_report 정리 ─────────────────────────────────────────
print("\n=== review_report 정리 ===")
for f in list(FINAL_DIR.glob("review_report_*.txt")):
    stem = f.stem[len("review_report_"):]
    if stem in rename_map:
        new_report = FINAL_DIR / f"review_report_{rename_map[stem]}.txt"
        f.rename(new_report)
        print(f"  ✅ {f.name} → {new_report.name}")
    else:
        f.unlink()
        print(f"  🗑️  삭제: {f.name}")

# ── 3. content_pipeline.json publish_order 업데이트 ───────────────
print("\n=== content_pipeline.json 업데이트 ===")
pipe = json.load(open(PIPELINE_FILE, encoding='utf-8'))

for new_num, old_stem, cluster, ct, week, slug in ORDER:
    sels = pipe.get('weekly_selections', {}).get(week, [])
    for sel in sels:
        if (sel.get('cluster_name') == cluster
                and sel.get('content_type', '').upper() == ct):
            old_order = sel.get('publish_order', '?')
            sel['publish_order'] = new_num
            print(f"  [{new_num:02d}] {cluster} [{ct}] (이전: {old_order})")
            break

pipe['_last_updated'] = datetime.datetime.utcnow().isoformat()
json.dump(pipe, open(PIPELINE_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print("\n✅ 완료")
