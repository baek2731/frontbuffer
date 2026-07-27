import os
import shutil

SRC = r"C:\Users\B\Projects\blogauto2"
DST = r"C:\Users\B\Projects\test"

# 복사할 파일 목록
groups = {
    "1": [
        "write.py", "publish_one.py", "research_gemini.py",
        "gemini_api.py", "gemini_review_api.py", "quality_check.py",
        "trends_analyzer.py", "step5_audit.py", "og_generator.py", "pipeline.py"
    ],
    "2": [
        "step1_research.yml", "step2_plan.yml", "step3_write.yml",
        "step4_publish.yml", "step4_check.yml", "step5_audit.yml",
        "notify.py", "posts_manager.py", "keyword_planner_analyzer.py", "monthly_analysis.py"
    ],
    "3": [
        "content_pipeline.json", "posts.json", "config.json"
    ]
}

# 폴더 생성
for g in groups:
    os.makedirs(os.path.join(DST, g), exist_ok=True)

# 재귀 탐색 후 복사
for group, filenames in groups.items():
    print(f"\n=== {group}차 ===")
    for fname in filenames:
        found = False
        for root, dirs, files in os.walk(SRC):
            # venv 폴더 제외
            dirs[:] = [d for d in dirs if d not in ("venv", ".git", "__pycache__", "node_modules")]
            if fname in files:
                src_path = os.path.join(root, fname)
                dst_path = os.path.join(DST, group, fname)
                shutil.copy2(src_path, dst_path)
                print(f"  복사: {src_path}")
                found = True
                break
        if not found:
            print(f"  없음: {fname}")

print("\n완료! C:\\Users\\B\\Projects\\test 확인해주세요.")
input("엔터를 누르면 종료...")
