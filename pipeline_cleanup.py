#!/usr/bin/env python3
# =====================================================================
# 🧹 파이프라인 상태 정리 (pipeline_cleanup.py)
# =====================================================================
# 목적: content_pipeline.json 에서 "이미 글이 나갔거나 중복이라 쓰지 말아야 하는데
#       candidate 로 남아 있는 기획안"을 discarded 로 바꿔 재작성(중복 글)을 막는다.
#
# 사용법 (저장소 루트에서):
#   python pipeline_cleanup.py            ← 미리보기만 (파일 수정 없음)
#   python pipeline_cleanup.py --apply    ← 실제 적용 (content_pipeline.json.bak 백업 생성)
# =====================================================================

import json
import shutil
import sys
from datetime import datetime, timezone

PIPELINE = "content_pipeline.json"

# (주차, 클러스터명, 유형, publish_order, 사유)
DISCARD = [
    ("2026-W32", "Samsung Galaxy Foldables", "COMPARISON", 17,
     "Fold 8 vs Flip 8 비교글이 이미 여러 편 발행됨 (중복 기획안)"),
    ("2026-W38", "Googlebooks Overview", "COMPARISON", 38,
     "Googlebook 모델 비교글이 10-02에 이미 발행됨 (중복 재생성)"),
    ("2026-W40", "Android Auto & Pixel Ecosystem", "GUIDE", 48,
     "Android Auto 문제 해결 가이드와 중복 — 필요한 부분만 기존 글에 병합"),
    ("2026-W30", "Google Gemini AI Features", "EXPLAINER", None,
     "Grade C(검색 수요 미검증)로 3개월 이상 대기 — 주제가 오래됨"),
    ("2026-W30", "Google Gemini AI Features", "GUIDE", None,
     "Grade C(검색 수요 미검증)로 3개월 이상 대기 — 주제가 오래됨"),
]


def main():
    apply = "--apply" in sys.argv
    data = json.load(open(PIPELINE, encoding="utf-8"))
    changed = 0
    for week, name, ct, order, reason in DISCARD:
        found = False
        for sel in data.get("weekly_selections", {}).get(week, []):
            if (sel.get("cluster_name") == name
                    and (sel.get("content_type") or "").upper() == ct
                    and (order is None or str(sel.get("publish_order")) == str(order))):
                found = True
                if sel.get("status") in ("candidate", "writing"):
                    print(f"{'적용' if apply else '대상'}: {week} {name} [{ct}] #{order}  "
                          f"{sel.get('status')} → discarded")
                    print(f"      사유: {reason}")
                    if apply:
                        sel["status"] = "discarded"
                        sel["discarded_at"] = datetime.now(timezone.utc).isoformat()
                        sel["discard_reason"] = reason
                    changed += 1
                else:
                    print(f"건너뜀(이미 {sel.get('status')}): {week} {name} [{ct}] #{order}")
        if not found:
            print(f"못 찾음: {week} {name} [{ct}] #{order}")

    # 참고: 오래 'writing' 상태로 멈춘 항목
    print("\n[참고] 'writing' 상태로 남은 항목 (Step 3 자동 선택 대상이 아니라 멈춰 있음)")
    for week, sels in sorted(data.get("weekly_selections", {}).items()):
        for sel in sels:
            if sel.get("status") == "writing":
                print(f"   - {week} {sel.get('cluster_name')} [{sel.get('content_type')}] "
                      f"{(sel.get('suggested_title') or '')[:60]}")

    if apply and changed:
        shutil.copyfile(PIPELINE, PIPELINE + ".bak")
        data["_last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(PIPELINE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ {changed}건 적용 완료 (백업: {PIPELINE}.bak)")
    elif apply:
        print("\nℹ️  바꿀 항목이 없습니다.")
    else:
        print(f"\n(미리보기) {changed}건 적용 대상. 실제로 바꾸려면: python pipeline_cleanup.py --apply")


if __name__ == "__main__":
    main()
