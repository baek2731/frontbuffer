# =====================================================================
# 🏗️ 새 환경 초기 세팅 (setup.py) — 1회 실행
# =====================================================================
# 사용법:
#   1. 새 폴더 생성 (예: C:\Users\B\Projects\blogauto2)
#   2. 아래 7개 파일을 새 폴더에 복사:
#      config.json, research.py, trends_analyzer.py, pipeline.py,
#      monthly_analysis.py, write.py, app.py, setup.py
#   3. python setup.py 실행
# =====================================================================

import os
import json

FOLDERS = [
    "research_data",
    "research_data/weekly",   # 주차별 리서치 파일 (주차 하위 폴더로 자동 생성)
    "research_data/trends",
    "research_data/write",
    "research_data/write/prompts",
    "research_data/write/drafts",
    "research_data/write/final",
    "research_data/write/published",
]

PIPELINE_INIT = {
    "_version": "1.3",
    "_description": "콘텐츠 파이프라인 — 클러스터 단위 관리",
    "_last_updated": "",
    "hub_clusters": {},
    "covered_clusters": {},
    "weekly_selections": {},
    "published": [],
}

GITIGNORE = """venv/
__pycache__/
.env
research_data/weekly/
research_data/trends/
research_data/write/drafts/
research_data/write/prompts/
# posts.json과 published/는 git으로 관리 (블로그 배포 시 필요)
"""

REQUIRED_FILES = [
    "config.json", "research.py", "pipeline.py", "write.py", "app.py",
    "posts_manager.py",
]
OPTIONAL_FILES = ["trends_analyzer.py", "monthly_analysis.py"]

print("=" * 60)
print("🏗️  Frontbuffer Editorial 새 환경 세팅")
print("=" * 60)

# 1. 폴더 생성
for d in FOLDERS:
    os.makedirs(d, exist_ok=True)
    print(f"✅ 폴더: {d}")

# 2. content_pipeline.json 초기화 (없을 때만)
if not os.path.exists("content_pipeline.json"):
    with open("content_pipeline.json", "w", encoding="utf-8") as f:
        json.dump(PIPELINE_INIT, f, ensure_ascii=False, indent=2)
    print("✅ content_pipeline.json 초기 생성")
else:
    print("ℹ️  content_pipeline.json 이미 존재 — 건너뜀")

# 3. posts.json 초기화 (없을 때만)
POSTS_INIT = {
    "_version":     "1.0",
    "_description": "발행된 글 전체 목록 — 허브+스포크 연결 관리",
    "posts":        [],
}
if not os.path.exists("posts.json"):
    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(POSTS_INIT, f, ensure_ascii=False, indent=2)
    print("✅ posts.json 초기 생성")
else:
    print("ℹ️  posts.json 이미 존재 — 건너뜀")

# 3. .gitignore
if not os.path.exists(".gitignore"):
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(GITIGNORE)
    print("✅ .gitignore 생성")

# 4. 필수 파일 확인
print("\n📋 파일 확인:")
missing = []
for f in REQUIRED_FILES:
    if os.path.exists(f):
        print(f"  ✅ {f}")
    else:
        print(f"  ❌ {f} — 없음! 복사 필요")
        missing.append(f)
for f in OPTIONAL_FILES:
    status = "✅" if os.path.exists(f) else "⬜ (선택)"
    print(f"  {status} {f}")

if missing:
    print(f"\n⚠️  필수 파일 {len(missing)}개 누락: {', '.join(missing)}")
else:
    print(f"""
🏁 세팅 완료! 다음 순서로 시작하세요:

  1. 가상환경 생성 + 패키지 설치:
     python -m venv venv
     venv\\Scripts\\activate
     pip install requests beautifulsoup4 lxml python-dotenv streamlit

  2. 주간 리서치:
     python research.py

  3. 앱 실행 (이후 브라우저에서 전체 조작):
     streamlit run app.py
""")
