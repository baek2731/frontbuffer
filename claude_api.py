# =====================================================================
# 🔍 Claude API 팩트체크 + 최종본 생성 (claude_api.py)
# =====================================================================
# 역할: write.py review가 생성한 review_prompt 파일을 읽어서
#       Claude API에 전송 → 최종본 받아서 final/{slug}_{TYPE}.md 저장
#
# 사용법:
#   python claude_api.py --cluster "Google Chrome Manifest V2 Migration" --type GUIDE
#   python claude_api.py --cluster "Steam Machine" --type HUB
#
# 환경변수:
#   ANTHROPIC_API_KEY: Claude API 키 (GitHub Secrets 또는 로컬 .env)
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
FINAL_DIR   = os.path.join(WRITE_DIR, "final")

# ── Claude API 설정 ───────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL      = "claude-sonnet-4-6"
CLAUDE_URL        = "https://api.anthropic.com/v1/messages"

# ── 재시도 설정 ───────────────────────────────────────────────────────
MAX_RETRIES = 3
RETRY_DELAY = 10


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def find_review_prompt(cluster_name, content_type):
    """write.py review가 생성한 review_prompt 파일 찾기."""
    slug = slugify(cluster_name)
    ct   = content_type.upper().strip()

    # 파일명 패턴: review_prompt_{slug}_{TYPE}.txt
    path = os.path.join(PROMPTS_DIR, f"review_prompt_{slug}_{ct}.txt")
    if os.path.exists(path):
        return path

    # fallback: TYPE 없는 버전
    fallback = os.path.join(PROMPTS_DIR, f"review_prompt_{slug}.txt")
    if os.path.exists(fallback):
        return fallback

    return None


def extract_final_markdown(response_text):
    """
    Claude 응답에서 ```markdown 코드블록 안의 최종본 추출.
    없으면 전체 텍스트 반환.
    """
    # ```markdown ... ``` 패턴
    match = re.search(r"```markdown\s*(.*?)```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # ``` ... ``` 패턴 (언어 없는 코드블록)
    match = re.search(r"```\s*(#.+?)```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 코드블록 없으면 전체 반환 (H1으로 시작하는 부분부터)
    h1_match = re.search(r"(^# .+)", response_text, re.MULTILINE)
    if h1_match:
        return response_text[h1_match.start():].strip()

    return response_text.strip()


def call_claude_api(prompt_text):
    """Claude API 호출 → 전체 응답 텍스트 반환."""
    if not ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY 환경변수가 없어요.")
        sys.exit(1)

    headers = {
        "x-api-key":         ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type":      "application/json",
    }
    payload = {
        "model":      CLAUDE_MODEL,
        "max_tokens": 8192,
        "messages": [
            {"role": "user", "content": prompt_text}
        ],
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"  🔍 Claude API 호출 중... (시도 {attempt}/{MAX_RETRIES})")
            resp = requests.post(CLAUDE_URL, headers=headers,
                                 json=payload, timeout=180)

            if resp.status_code == 200:
                data    = resp.json()
                content = data.get("content", [])
                text    = "".join(
                    c.get("text", "") for c in content
                    if c.get("type") == "text"
                ).strip()
                if text:
                    # 사용량 로그
                    usage = data.get("usage", {})
                    print(f"  📊 토큰 사용: "
                          f"입력 {usage.get('input_tokens', 0):,} / "
                          f"출력 {usage.get('output_tokens', 0):,}")
                    return text
                print("  ⚠️ 응답 텍스트 비어있음")

            elif resp.status_code == 429:
                print(f"  ⚠️ 속도 제한 (429) — {RETRY_DELAY}초 후 재시도")
                time.sleep(RETRY_DELAY)

            elif resp.status_code == 529:
                print(f"  ⚠️ 과부하 (529) — {RETRY_DELAY}초 후 재시도")
                time.sleep(RETRY_DELAY)

            elif resp.status_code == 401:
                print(f"  ❌ 인증 실패 (401) — ANTHROPIC_API_KEY 확인 필요")
                sys.exit(1)

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


def save_final(final_text, cluster_name, content_type):
    """최종본을 final/{slug}_{TYPE}.md 저장."""
    os.makedirs(FINAL_DIR, exist_ok=True)
    slug       = slugify(cluster_name)
    ct         = content_type.upper().strip()
    final_path = os.path.join(FINAL_DIR, f"{slug}_{ct}.md")

    with open(final_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    return final_path


def check_final_quality(final_text):
    """최종본 품질 체크."""
    word_count = len(final_text.split())
    errors     = []
    warnings   = []

    if word_count < 600:
        errors.append(f"단어 수 {word_count}개 — 600 미만")
    elif word_count < 800:
        warnings.append(f"단어 수 {word_count}개 — 800 미만")

    nv_count = len(re.findall(r"\[NEEDS VERIFICATION\]", final_text))
    if nv_count > 0:
        errors.append(f"[NEEDS VERIFICATION] {nv_count}개 미해소")

    return {"ok": len(errors) == 0, "errors": errors,
            "warnings": warnings, "word_count": word_count}


def main():
    parser = argparse.ArgumentParser(description="Claude API 팩트체크 + 최종본 생성")
    parser.add_argument("--cluster", required=True, help="클러스터명")
    parser.add_argument("--type",    required=True, help="content_type")
    args = parser.parse_args()

    cluster_name = args.cluster
    content_type = args.type.upper()

    print(f"\n{'='*60}")
    print(f"🔍 Claude API 팩트체크 + 최종본: {cluster_name} [{content_type}]")
    print(f"{'='*60}")
    print(f"  모델: {CLAUDE_MODEL}")

    # 1. review_prompt 파일 찾기
    prompt_path = find_review_prompt(cluster_name, content_type)
    if not prompt_path:
        print(f"❌ review_prompt 파일 없음 — write.py review 먼저 실행하세요.")
        print(f"   탐색 경로: {PROMPTS_DIR}/review_prompt_{slugify(cluster_name)}_{content_type}.txt")
        sys.exit(1)

    print(f"  📄 리뷰 프롬프트: {prompt_path}")
    prompt_text = open(prompt_path, encoding="utf-8").read()
    print(f"  📏 프롬프트 크기: {len(prompt_text.encode())/1024:.1f} KB")

    # 2. Claude API 호출
    start         = time.time()
    response_text = call_claude_api(prompt_text)
    elapsed       = time.time() - start

    if not response_text:
        print("❌ 최종본 생성 실패 — API 응답 없음")
        sys.exit(1)

    print(f"  ✅ API 응답 완료 ({elapsed:.1f}초)")

    # 3. 최종본 추출 (markdown 코드블록에서)
    final_text = extract_final_markdown(response_text)
    print(f"  📝 최종본 추출 완료 ({len(final_text.split())}단어)")

    # 4. 품질 체크
    quality = check_final_quality(final_text)
    print(f"  📊 단어 수: {quality['word_count']}개")
    for w in quality["warnings"]:
        print(f"  ⚠️  {w}")
    for e in quality["errors"]:
        print(f"  ❌ {e}")

    if not quality["ok"]:
        # 에러가 있어도 일단 저장하고 경고만 출력
        # (사람이 확인 후 처리할 수 있도록)
        print("⚠️  품질 경고 있음 — 저장은 진행 (수동 확인 필요)")

    # 5. 최종본 저장
    final_path = save_final(final_text, cluster_name, content_type)
    print(f"  💾 최종본 저장: {final_path}")

    # 6. 판정 리포트도 별도 저장 (한국어 리포트 포함 전체 응답)
    slug        = slugify(cluster_name)
    ct          = content_type.upper().strip()
    report_path = os.path.join(FINAL_DIR, f"review_report_{slug}_{ct}.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(response_text)
    print(f"  📋 판정 리포트: {report_path}")

    # 7. 결과 JSON 출력
    result = {
        "ok":           quality["ok"],
        "cluster":      cluster_name,
        "content_type": content_type,
        "final_path":   final_path,
        "report_path":  report_path,
        "word_count":   quality["word_count"],
        "warnings":     quality["warnings"],
        "errors":       quality["errors"],
        "elapsed":      round(elapsed, 1),
        "timestamp":    datetime.now(timezone.utc).isoformat(),
    }
    print(f"\n✅ 완료: {json.dumps(result, ensure_ascii=False)}")

    # 다음 단계 안내
    print(f"""
다음 단계:
  python write.py done "{cluster_name}" --type {content_type}
""")


if __name__ == "__main__":
    main()
