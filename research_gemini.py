# =====================================================================
# 🤖 Gemini 1차 호출 — 리서치 → 기획안 JSON (research_gemini.py)
# =====================================================================
# 역할: research.py가 생성한 weekly/{week}/prompt.txt를 읽어서
#       Gemini API 1차 호출 → 기획안 JSON 받기
#       → ai_result_latest.json 저장
#       → record_selections() 자동 호출 → content_pipeline.json 업데이트
#
# 사용법:
#   python research_gemini.py              ← 이번 주 자동
#   python research_gemini.py 2026-W29    ← 특정 주차 지정
#
# 환경변수:
#   GEMINI_API_KEY: Gemini API 키
# =====================================================================

import os
import re
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone

import requests

# ── 경로 설정 ─────────────────────────────────────────────────────────
OUTPUT_DIR  = "research_data"
WEEKLY_DIR  = os.path.join(OUTPUT_DIR, "weekly")
AI_RESULT   = os.path.join(OUTPUT_DIR, "ai_result_latest.json")

# ── Gemini API 설정 ───────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL     = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={{api_key}}"
)

MAX_RETRIES = 3
RETRY_DELAY = 10


def get_week_tag():
    return datetime.now(timezone.utc).strftime("%Y-W%W")


def find_prompt_file(week_tag):
    """weekly/{week_tag}/prompt.txt 찾기."""
    path = os.path.join(WEEKLY_DIR, week_tag, "prompt.txt")
    if os.path.exists(path):
        return path
    # 가장 최신 주차 폴더 fallback
    weeks = sorted(Path(WEEKLY_DIR).glob("*/prompt.txt"), reverse=True)
    if weeks:
        print(f"  ℹ️  {week_tag} 프롬프트 없음 → 최신 폴더 사용: {weeks[0]}")
        return str(weeks[0])
    return None


def call_gemini(prompt_text):
    """Gemini API 호출 → 텍스트 반환."""
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY 환경변수가 없어요.")
        sys.exit(1)

    url     = GEMINI_URL.format(api_key=GEMINI_API_KEY)
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "temperature":     0.7,
            "maxOutputTokens": 8192,
        }
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"  🤖 Gemini API 호출 중... (시도 {attempt}/{MAX_RETRIES})")
            resp = requests.post(url, json=payload, timeout=120)

            if resp.status_code == 200:
                data       = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    print("  ⚠️ candidates 없음")
                    continue
                parts = candidates[0].get("content", {}).get("parts", [])
                text  = "".join(p.get("text", "") for p in parts).strip()
                if text:
                    return text
                print("  ⚠️ 응답 텍스트 비어있음")

            elif resp.status_code == 429:
                print(f"  ⚠️ 속도 제한 (429) — {RETRY_DELAY}초 후 재시도")
                time.sleep(RETRY_DELAY)
            elif resp.status_code == 503:
                print(f"  ⚠️ 서비스 불가 (503) — {RETRY_DELAY}초 후 재시도")
                time.sleep(RETRY_DELAY)
            else:
                print(f"  ❌ API 오류 {resp.status_code}: {resp.text[:200]}")
                break

        except requests.exceptions.Timeout:
            print(f"  ⚠️ 타임아웃 — {RETRY_DELAY}초 후 재시도")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"  ❌ 예외: {e}")
            break

    return None


def parse_json_response(text):
    """
    Gemini 응답에서 JSON 배열 추출.
    markdown fence(```json ... ```) 또는 raw JSON 모두 처리.
    """
    # ```json ... ``` 제거
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    # JSON 배열 부분만 추출
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        text = match.group(0)

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        print(f"  ⚠️ JSON 파싱 성공했지만 배열이 아님: {type(data)}")
        return None
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON 파싱 실패: {e}")
        print(f"  원문 일부: {text[:300]}")
        return None


def add_data_grade(selections):
    """
    data_grade 자동 부여.
    evergreen_score 기반: 85+ → A, 70+ → B, 나머지 → C
    """
    for sel in selections:
        score = sel.get("evergreen_score", 0)
        if score >= 85:
            sel["data_grade"] = "A"
        elif score >= 70:
            sel["data_grade"] = "B"
        else:
            sel["data_grade"] = "C"
    return selections


def main():
    parser = argparse.ArgumentParser(description="Gemini 1차 호출 — 리서치 → 기획안")
    parser.add_argument("week_tag", nargs="?", default=None, help="주차 태그 (예: 2026-W29)")
    args     = parser.parse_args()
    week_tag = args.week_tag or get_week_tag()

    print(f"\n{'='*60}")
    print(f"🤖 Gemini 1차 호출 — 리서치 기획안 생성: {week_tag}")
    print(f"{'='*60}")
    print(f"  모델: {GEMINI_MODEL}")

    # 1. 프롬프트 파일 찾기
    prompt_path = find_prompt_file(week_tag)
    if not prompt_path:
        print(f"❌ research.py를 먼저 실행하세요.")
        print(f"   탐색 경로: {WEEKLY_DIR}/{week_tag}/prompt.txt")
        sys.exit(1)

    print(f"  📄 프롬프트: {prompt_path}")
    prompt_text = open(prompt_path, encoding="utf-8").read()
    print(f"  📏 크기: {len(prompt_text.encode())/1024:.1f} KB")

    # 2. Gemini API 호출
    start    = time.time()
    response = call_gemini(prompt_text)
    elapsed  = time.time() - start

    if not response:
        print("❌ Gemini 응답 없음")
        sys.exit(1)

    print(f"  ✅ 응답 완료 ({elapsed:.1f}초)")

    # 3. JSON 파싱
    selections = parse_json_response(response)
    if not selections:
        print("❌ JSON 파싱 실패 — 원문 저장 후 종료")
        raw_path = os.path.join(WEEKLY_DIR, week_tag, "gemini_raw_response.txt")
        open(raw_path, "w", encoding="utf-8").write(response)
        print(f"   원문: {raw_path}")
        sys.exit(1)

    print(f"  📊 기획안 {len(selections)}개 파싱 완료")

    # 4. data_grade 자동 부여
    selections = add_data_grade(selections)
    grade_a = sum(1 for s in selections if s.get("data_grade") == "A")
    grade_b = sum(1 for s in selections if s.get("data_grade") == "B")
    grade_c = sum(1 for s in selections if s.get("data_grade") == "C")
    print(f"  📈 Grade: A={grade_a} B={grade_b} C={grade_c}")

    # 5. ai_result_latest.json 저장
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(AI_RESULT, "w", encoding="utf-8") as f:
        json.dump(selections, f, ensure_ascii=False, indent=2)
    print(f"  💾 ai_result_latest.json 저장: {len(selections)}개")

    # 6. Trends/KP CSV 있으면 trends_analyzer 자동 실행 → Grade 재판정
    print(f"\n  📈 Trends/KP CSV 확인 중...")
    trends_dir = os.path.join("research_data", "trends", week_tag)
    has_trends_csv = False
    has_kp_csv     = False

    if os.path.isdir(trends_dir):
        for root, dirs, files in os.walk(trends_dir):
            for f in files:
                if f.endswith(".csv"):
                    fpath = os.path.join(root, f)
                    rel   = os.path.relpath(fpath, trends_dir)
                    # 루트 직속 csv = KP, 하위 폴더 csv = Trends
                    if os.sep not in rel and "/" not in rel:
                        has_kp_csv = True
                        print(f"    📊 KP CSV 감지: {f}")
                    else:
                        has_trends_csv = True
                        print(f"    📈 Trends CSV 감지: {rel}")

    if not has_trends_csv and not has_kp_csv:
        print(f"\n❌ Trends/KP CSV 없음 — Step 2를 중단합니다.")
        print(f"   manual_report.md의 추천 키워드를 Google Trends에서 검색 후")
        print(f"   CSV를 research_data/trends/{week_tag}/{{폴더명}}/ 에 업로드하세요.")
        print(f"   KP CSV는 research_data/trends/{week_tag}/ 루트에 업로드하세요.")
        sys.exit(1)

    print(f"  ✅ CSV 감지 — trends_analyzer.py 실행 중...")
    try:
        import trends_analyzer
        report = trends_analyzer.analyze_week(week_tag, update_pipeline=True)
        print(f"  ✅ Trends/KP 분석 완료")
        for cluster in report.get("clusters", []):
            grade   = cluster.get("grade", "?")
            name    = cluster.get("cluster_name", "")
            pattern = cluster.get("trends_pattern", "UNKNOWN")
            reasons = " | ".join(cluster.get("grade_reasons", []))
            print(f"    [{grade}] {name} — {pattern}")
            print(f"         {reasons}")
    except Exception as e:
        print(f"  ⚠️ trends_analyzer 실행 실패: {e}")

    # 7. Grade 기반 기획안 선정/폐기
    # content_pipeline에서 최신 Grade 다시 로드 (trends_analyzer가 업데이트했을 수 있음)
    try:
        import json as _json
        _pipe = _json.load(open("content_pipeline.json", encoding="utf-8"))
        _week_sels = _pipe.get("weekly_selections", {}).get(week_tag, [])
        # selections의 data_grade를 pipeline의 최신값으로 갱신
        for sel in selections:
            for ps in _week_sels:
                if ps.get("cluster_name") == sel.get("cluster_name"):
                    sel["data_grade"] = ps.get("data_grade", sel.get("data_grade", "C"))
                    break
    except Exception:
        pass

    grade_a = [s for s in selections if s.get("data_grade") == "A"]
    grade_b = [s for s in selections if s.get("data_grade") == "B"]
    grade_c = [s for s in selections if s.get("data_grade") == "C"]

    print(f"\n  📊 최종 Grade 판정:")
    print(f"    Grade A (발행 확정): {len(grade_a)}개")
    for s in grade_a:
        print(f"      ✅ {s.get('cluster_name')} [{s.get('content_type')}]")
    print(f"    Grade B (발행 가능): {len(grade_b)}개")
    for s in grade_b:
        print(f"      🔶 {s.get('cluster_name')} [{s.get('content_type')}]")
    print(f"    Grade C (폐기): {len(grade_c)}개")
    for s in grade_c:
        print(f"      ❌ {s.get('cluster_name')} [{s.get('content_type')}] → 파이프라인 제외")

    # Grade C는 status → rejected로 마킹
    if grade_c:
        try:
            import json as _json2
            _pipe2 = _json2.load(open("content_pipeline.json", encoding="utf-8"))
            _changed = False
            for week_key, sels in _pipe2.get("weekly_selections", {}).items():
                for sel in sels:
                    if (sel.get("data_grade") == "C"
                            and sel.get("status") == "candidate"):
                        sel["status"] = "rejected"
                        _changed = True
            if _changed:
                _pipe2["_last_updated"] = datetime.now(timezone.utc).isoformat()
                _json2.dump(_pipe2, open("content_pipeline.json", "w", encoding="utf-8"),
                            ensure_ascii=False, indent=2)
                print(f"  ✅ Grade C {len(grade_c)}개 → status: rejected 처리")
        except Exception as e:
            print(f"  ⚠️ rejected 마킹 실패: {e}")

    # Grade A/B만 자동 선택 → content_pipeline.json 등록
    auto_select = grade_a + grade_b
    print(f"\n  🔷 자동 선택 (Grade A/B): {len(auto_select)}개")

    if auto_select:
        try:
            from pipeline import record_selections
            result = record_selections(auto_select, week_tag=week_tag)
            if result.get("ok"):
                print(f"  ✅ content_pipeline.json 등록 완료")
                print(f"     신규: {result.get('recorded', 0)}개 | 중복 스킵: {result.get('skipped', 0)}개")
            else:
                print(f"  ⚠️ 등록 실패: {result.get('error', '')}")
        except Exception as e:
            print(f"  ⚠️ record_selections 실패: {e}")
    else:
        print("  ⚠️ Grade A/B 기획안 없음 — content_pipeline.json 업데이트 생략")

    # 7. 결과 저장 (Actions 로그용)
    result_summary = {
        "ok":           True,
        "week_tag":     week_tag,
        "total":        len(selections),
        "grade_a":      grade_a,
        "grade_b":      grade_b,
        "grade_c":      grade_c,
        "auto_selected": len(auto_select),
        "elapsed":      round(elapsed, 1),
        "timestamp":    datetime.now(timezone.utc).isoformat(),
    }

    summary_path = os.path.join(WEEKLY_DIR, week_tag, "research_gemini_result.json")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result_summary, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 완료: {json.dumps(result_summary, ensure_ascii=False)}")
    print(f"""
다음 단계:
  python trends_analyzer.py {week_tag}   ← Trends CSV 있으면 실행
  python write.py prep "[클러스터명]"    ← 글쓰기 시작
""")


if __name__ == "__main__":
    main()
