"""
W30 전체 초기화 스크립트

삭제:
  - research_data/trends/2026-W30/ (CSV + 폴더)
  - research_data/weekly/2026-W30/ (prompt, 기획안)
  - research_data/write/drafts/ (W30 초안)
  - research_data/write/prompts/ (W30 프롬프트)
  - content_pipeline.json W30 항목 전체 제거

유지:
  - _posts/ 14편
  - research_data/write/final/ 9편
  - posts.json
"""

import os
import json
import shutil
from datetime import datetime, timezone

ROOT = r"C:\Users\B\Projects\blogauto2"
WEEK = "2026-W30"

print("=" * 60)
print(f"W30 전체 초기화 시작")
print("=" * 60)

# ── 1. research_data/trends/2026-W30/ 삭제 ─────────────────────────
trends_dir = os.path.join(ROOT, "research_data", "trends", WEEK)
if os.path.exists(trends_dir):
    shutil.rmtree(trends_dir)
    print(f"✅ 삭제: {trends_dir}")
else:
    print(f"ℹ️  없음: {trends_dir}")

# ── 2. research_data/weekly/2026-W30/ 삭제 ─────────────────────────
weekly_dir = os.path.join(ROOT, "research_data", "weekly", WEEK)
if os.path.exists(weekly_dir):
    shutil.rmtree(weekly_dir)
    print(f"✅ 삭제: {weekly_dir}")
else:
    print(f"ℹ️  없음: {weekly_dir}")

# ── 3. research_data/write/drafts/ 전체 삭제 ───────────────────────
drafts_dir = os.path.join(ROOT, "research_data", "write", "drafts")
if os.path.exists(drafts_dir):
    shutil.rmtree(drafts_dir)
    os.makedirs(drafts_dir)
    print(f"✅ 초기화: {drafts_dir}")
else:
    print(f"ℹ️  없음: {drafts_dir}")

# ── 4. research_data/write/prompts/ 전체 삭제 ──────────────────────
prompts_dir = os.path.join(ROOT, "research_data", "write", "prompts")
if os.path.exists(prompts_dir):
    shutil.rmtree(prompts_dir)
    os.makedirs(prompts_dir)
    print(f"✅ 초기화: {prompts_dir}")
else:
    print(f"ℹ️  없음: {prompts_dir}")

# ── 5. content_pipeline.json W30 항목 제거 ─────────────────────────
pipeline_file = os.path.join(ROOT, "content_pipeline.json")
with open(pipeline_file, encoding="utf-8") as f:
    data = json.load(f)

w30_count = len(data.get("weekly_selections", {}).get(WEEK, []))
if WEEK in data.get("weekly_selections", {}):
    del data["weekly_selections"][WEEK]
    print(f"✅ content_pipeline.json W30 항목 {w30_count}개 제거")

# analysis_result.json도 정리
analysis_file = os.path.join(ROOT, "research_data", "trends", f"analysis_result_{WEEK}.json")
if os.path.exists(analysis_file):
    os.remove(analysis_file)
    print(f"✅ 삭제: {analysis_file}")

data["_last_updated"] = datetime.now(timezone.utc).isoformat()
with open(pipeline_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"✅ content_pipeline.json 저장 완료")

print()
print("=" * 60)
print("초기화 완료!")
print()
print("유지된 것:")
print("  _posts/ 14편 — 그대로")
print("  research_data/write/final/ — 그대로")
print("  posts.json — 그대로")
print()
print("다음 단계:")
print("  git add -A")
print("  git commit -m 'fix: W30 전체 초기화 — 코드 정비 후 재시도'")
print("  git push origin main")
print("=" * 60)

input("\n엔터를 누르면 종료...")
