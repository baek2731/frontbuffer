# =====================================================================
# 🤖 Gemini API 초안 생성 (gemini_api.py)
# =====================================================================
# 역할: write.py prep이 생성한 write_prompt 파일을 읽어서
#       Gemini API에 전송 → 초안 받아서 drafts/{slug}.md 저장
#
# 사용법:
#   python gemini_api.py --cluster "Google Chrome Manifest V2 Migration" --type GUIDE
#   python gemini_api.py --cluster "Steam Machine" --type HUB
#
# 환경변수:
#   GEMINI_API_KEY: Gemini API 키 (GitHub Secrets 또는 로컬 .env)
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

# ── 경로 설정 (write.py와 동일) ──────────────────────────────────────
WRITE_DIR   = os.path.join("research_data", "write")
PROMPTS_DIR = os.path.join(WRITE_DIR, "prompts")
DRAFTS_DIR  = os.path.join(WRITE_DIR, "drafts")

# ── Gemini API 설정 ───────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL     = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={{api_key}}"
)

# ── 재시도 설정 ───────────────────────────────────────────────────────
MAX_RETRIES    = 3
RETRY_DELAY    = 10  # 초


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def find_prompt_file(cluster_name, content_type, file_id=None):
    """
    write.py prep이 생성한 write_prompt 파일 찾기.
    file_id 기반으로 탐색 (slug 불일치 완전 방지).
    반환: prompt_path (str) or None
    """
    ct = content_type.upper().strip()

    # 1순위: file_id 직접 매칭 (folder_id + week_tag 체계)
    if file_id:
        path = os.path.join(PROMPTS_DIR, f"write_prompt_{file_id}.txt")
        if os.path.exists(path):
            return path

    # 2순위: slug 기반 매칭 (하위 호환)
    slug = slugify(cluster_name)
    matches = sorted(Path(PROMPTS_DIR).glob(f"write_prompt_*_{slug}_{ct}*.txt"), reverse=True)
    if not matches:
        matches = sorted(Path(PROMPTS_DIR).glob(f"write_prompt_{slug}_{ct}*.txt"), reverse=True)
    if matches:
        return str(matches[0])

    # 3순위: 퍼지 매칭 — slug 단어 기반
    slug_words = set(slug.split("-")) - {"a", "an", "the", "and", "or", "of"}
    cands = sorted(Path(PROMPTS_DIR).glob(f"write_prompt_*.txt"), reverse=True)
    for cand in cands:
        fname_words = set(cand.stem.split("-").copy())
        # CT 매칭 + slug 단어 절반 이상
        if ct.lower() in cand.stem.lower():
            if len(slug_words & fname_words) >= max(1, len(slug_words) // 2):
                print(f"  ⚠️  퍼지 매칭: {cand.name}")
                return str(cand)

    return None


def call_gemini_api(prompt_text):
    """Gemini API 호출 → 텍스트 반환."""
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY 환경변수가 없어요.")
        sys.exit(1)

    url     = GEMINI_URL.format(api_key=GEMINI_API_KEY)
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_text}]
            }
        ],
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
                data = resp.json()
                # 응답에서 텍스트 추출
                candidates = data.get("candidates", [])
                if not candidates:
                    print("  ⚠️ 응답에 candidates 없음")
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
            print(f"  ❌ 예외 발생: {e}")
            break

    return None


def save_draft(draft_text, file_id, content_type):
    """초안을 drafts/{file_id}.md 저장. file_id는 write.py get_file_id() 반환값."""
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    draft_path = os.path.join(DRAFTS_DIR, f"{file_id}.md")

    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(draft_text)

    return draft_path


def check_draft_quality(draft_text):
    """기본 품질 체크."""
    word_count = len(draft_text.split())
    errors     = []
    warnings   = []

    if word_count < 600:
        errors.append(f"단어 수 {word_count}개 — 600 미만")
    elif word_count < 800:
        warnings.append(f"단어 수 {word_count}개 — 800 미만 (review에서 보강 필요)")

    nv_count = len(re.findall(r"\[NEEDS VERIFICATION\]", draft_text))
    if nv_count > 0:
        # 경고만 출력 — Claude 검증 단계에서 해소하므로 에러 처리 안 함
        warnings.append(f"[NEEDS VERIFICATION] {nv_count}개 → Claude 검증에서 해소 예정")

    return {"ok": len(errors) == 0, "errors": errors,
            "warnings": warnings, "word_count": word_count}


def main():
    parser = argparse.ArgumentParser(description="Gemini API 초안 생성")
    parser.add_argument("--cluster", required=True, help="클러스터명")
    parser.add_argument("--type",    required=True, help="content_type (GUIDE/LISTICLE/COMPARISON/EXPLAINER/HUB)")
    parser.add_argument("--file-id", default=None,  dest="file_id",
                        help="folder_id+week_tag 기반 파일 ID (step3에서 자동 전달)")
    args = parser.parse_args()

    cluster_name = args.cluster
    content_type = args.type.upper()

    print(f"\n{'='*60}")
    print(f"🤖 Gemini API 초안 생성: {cluster_name} [{content_type}]")
    print(f"{'='*60}")
    print(f"  모델: {GEMINI_MODEL}")

    # 1. 프롬프트 파일 찾기 (file_id 기반 — slug 불일치 방지)
    file_id     = args.file_id if hasattr(args, "file_id") and args.file_id else None
    prompt_path = find_prompt_file(cluster_name, content_type, file_id=file_id)
    if not prompt_path:
        print(f"❌ write_prompt 파일 없음 — write.py prep 먼저 실행하세요.")
        print(f"   탐색 경로: {PROMPTS_DIR}/write_prompt_*.txt")
        sys.exit(1)

    # file_id를 프롬프트 파일명에서 역추출
    fname_stem = Path(prompt_path).stem  # write_prompt_{file_id}
    file_id    = fname_stem[len("write_prompt_"):]

    print(f"  📄 프롬프트: {prompt_path}")
    print(f"  🔑 file_id: {file_id}")
    prompt_text = open(prompt_path, encoding="utf-8").read()
    print(f"  📏 프롬프트 크기: {len(prompt_text.encode())/1024:.1f} KB")

    # 2. Gemini API 호출 + 품질 미달 시 내부 재생성 (최대 3회)
    #    이유: Gemini가 간헐적으로 소스 리포트만 출력하고 본문을 생략함
    #          (113/507단어 실패 사례). prep 재실행 없이 같은 프롬프트로
    #          재시도하면 대부분 해결되고, 루프 전체 재시작 비용을 아낀다.
    MAX_GEN_ATTEMPTS = 3
    start      = time.time()
    draft_text = None
    quality    = None

    for gen_attempt in range(1, MAX_GEN_ATTEMPTS + 1):
        if gen_attempt > 1:
            print(f"  🔄 품질 미달 — 재생성 시도 {gen_attempt}/{MAX_GEN_ATTEMPTS}")
        candidate = call_gemini_api(prompt_text)
        if not candidate:
            continue
        q = check_draft_quality(candidate)
        print(f"  📊 단어 수: {q['word_count']}개")
        if q["ok"]:
            draft_text, quality = candidate, q
            break
        # 미달이어도 지금까지 중 가장 긴 결과는 보관 (전부 실패 시 대비)
        if draft_text is None or q["word_count"] > quality["word_count"]:
            draft_text, quality = candidate, q

    elapsed = time.time() - start

    if not draft_text:
        print("❌ 초안 생성 실패 — API 응답 없음")
        sys.exit(1)

    print(f"  ✅ 초안 생성 완료 ({elapsed:.1f}초, {gen_attempt}회 시도)")
    for w in quality["warnings"]:
        print(f"  ⚠️  {w}")
    for e in quality["errors"]:
        print(f"  ❌ {e}")

    if not quality["ok"]:
        print("⚠️  품질 기준 미달 — 저장은 진행 (gemini_review_api 단계에서 재생성 가능)")
        # exit(1) 제거: 미달이어도 review 단계에서 보강 가능하므로 루프 계속

    # 4. 초안 저장 — file_id 사용 (write.py와 파일명 일치)
    draft_path = save_draft(draft_text, file_id, content_type)
    print(f"  💾 초안 저장: {draft_path}")

    # 5. 결과 JSON 출력 (pipeline.yml에서 파싱용)
    result = {
        "ok":           True,
        "cluster":      cluster_name,
        "content_type": content_type,
        "draft_path":   draft_path,
        "word_count":   quality["word_count"],
        "warnings":     quality["warnings"],
        "elapsed":      round(elapsed, 1),
        "timestamp":    datetime.now(timezone.utc).isoformat(),
    }
    print(f"\n✅ 완료: {json.dumps(result, ensure_ascii=False)}")

    # 다음 단계 안내
    print(f"""
다음 단계:
  python write.py review "{cluster_name}" --type {content_type}
  python gemini_review_api.py --cluster "{cluster_name}" --type {content_type}
""")


if __name__ == "__main__":
    main()
