import os
import re

posts_dir = r"C:\Users\B\Projects\blogauto2\_posts"

targets = [
    "2026-07-15-steam-machine-led-error-codes-what-each-warning-light-actually-means.md",
    "2026-07-16-how-to-backup-samsung-health-data-before-account-deletion.md",
    "2026-07-17-samsung-health-vs-google-health-connect-feature-comparison.md",
    "2026-07-21-android-ecosystem_explainer.md",
    "2026-07-22-android-ecosystem_guide.md",
    "2026-07-23-fallout-series_comparison.md",
    "2026-07-24-fallout-series_explainer.md",
    "2026-07-26-fallout-series_guide.md",
    "2026-07-28-portable-gaming_explainer.md",
    "2026-07-29-samsung-health-data-ecosystem_hub.md",
    "2026-07-30-steam-machine-hardware-management_hub.md",
    "2026-08-02-01-galaxy-fold_explainer.md",
    "2026-08-03-01-galaxy-fold_guide.md",
    "2026-08-05-samsung-galaxy-z-foldflip-series_explainer.md",
    "2026-08-08-06-android-auto_comparison.md",
]

for filename in targets:
    path = os.path.join(posts_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines(keepends=True)
    changed = False
    new_lines = []
    for line in lines:
        if line.strip().startswith("excerpt:") and "—" in line:
            new_line = line.replace("—", "-")
            new_lines.append(new_line)
            changed = True
        else:
            new_lines.append(line)

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"[수정] {filename}")
    else:
        print(f"[스킵] {filename}")

print("\n완료")
