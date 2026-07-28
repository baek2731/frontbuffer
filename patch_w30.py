import json

pipe = json.load(open("content_pipeline.json", encoding="utf-8"))

folder_map = {
    "Samsung Galaxy Fold 8 Features": "01-galaxy-fold",
    "Android Auto Troubleshooting":   "06-android-auto",
    "Gaming Media Formats":           "",
}

for sel in pipe.get("weekly_selections", {}).get("2026-W30", []):
    name = sel.get("cluster_name", "")
    if name in folder_map and not sel.get("folder"):
        sel["folder"] = folder_map[name]

pipe["_last_updated"] = "2026-07-28T manual-patch"
json.dump(pipe, open("content_pipeline.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("완료")
