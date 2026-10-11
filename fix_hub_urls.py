#!/usr/bin/env python3
# =====================================================================
# 🔗 파이프라인의 허브 주소 바로잡기 (fix_hub_urls.py)
# =====================================================================
# content_pipeline.json 의 hub_clusters[*].hub_url 이 파일명 기준(…_hub/)으로 잘못 기록돼 있으면
# 실제 발행된 허브 글의 주소로 고친다. (Samsung Health: …ecosystem_hub/ → …ecosystem/)
# 이 값은 Step 5 의 허브 푸터와 publish_one.py 의 스포크→허브 링크에 쓰인다.
#
# 사용법 (저장소 루트에서):
#   python fix_hub_urls.py            ← 미리보기
#   python fix_hub_urls.py --apply    ← 적용 (content_pipeline.json.bak 백업 생성)
# =====================================================================

import json
import re
import shutil
import sys
from pathlib import Path

PIPELINE = "content_pipeline.json"
POSTS = Path("_posts")
SITE = "https://frontbuffer.net"
APPLY = "--apply" in sys.argv


def key(url):
    return re.sub(r"_hub$", "", url.rstrip("/").split("/")[-1].lower())


def real_hub_urls():
    out = {}
    for p in sorted(POSTS.glob("*.md")):
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        fm = m.group(1) if m else ""
        if not (p.stem.lower().endswith("_hub") or re.search(r"^tags:.*[\"']hub[\"']", fm, re.M | re.I)):
            continue
        pm = re.search(r"^permalink:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", fm, re.M)
        if pm:
            path = pm.group(1).strip()
        else:
            cm = re.search(r"^categories:\s*\[(.+?)\]", fm, re.M)
            cat = cm.group(1).split(",")[0].strip().strip("\"'") if cm else "tech"
            path = f"/{cat}/{p.stem[11:].rstrip('-')}/"
        url = SITE + (path if path.endswith("/") else path + "/")
        out[key(url)] = url
    return out


def main():
    data = json.load(open(PIPELINE, encoding="utf-8"))
    real = real_hub_urls()
    print(f"_posts 에서 찾은 허브 글: {len(real)}개")
    changed = 0
    for name, info in data.get("hub_clusters", {}).items():
        cur = info.get("hub_url", "")
        if not cur or cur == "PENDING" or not cur.startswith("http"):
            continue
        want = real.get(key(cur))
        if want and want != cur:
            print(f"{'적용' if APPLY else '대상'}: {name}\n   {cur}\n → {want}")
            if APPLY:
                info["hub_url"] = want
            changed += 1
        elif not want:
            print(f"확인 필요(_posts 에서 대응하는 허브 글을 못 찾음): {name} → {cur}")
    if changed and APPLY:
        shutil.copyfile(PIPELINE, PIPELINE + ".bak")
        with open(PIPELINE, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        print(f"\n✅ {changed}건 적용 (백업: {PIPELINE}.bak)")
    elif not changed:
        print("\nℹ️  바꿀 항목이 없습니다.")
    else:
        print("\n적용하려면: python fix_hub_urls.py --apply")


if __name__ == "__main__":
    main()
