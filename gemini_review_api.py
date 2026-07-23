# =====================================================================
# 🤖 Gemini API 팩트체크 + 최종본 생성 (gemini_review_api.py)
# =====================================================================
# 역할: write.py review가 생성한 review_prompt 파일을 읽어서
#       Gemini API에 전송 → 최종본 받아서 final/{slug}_{TYPE}.md 저장
#
# 사용법:
#   python gemini_review_api.py --cluster "Fallout Series" --type COMPARISON
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
WRITE_DIR   = os.path.join("research_data", "write")
PROMPTS_DIR = os.path.join(WRITE_DIR, "prompts")
FINAL_DIR   = os.path.join(WRITE_DIR, "final")

# ── Gemini API 설정 ───────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL     = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={{api_key}}"
)

MAX_RETRIES = 3
RETRY_DELAY = 10


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def find_review_prompt(cluster_name, content_type):
    slug = slugify(cluster_name)
    ct   = content_type.upper().strip()
    path = os.path.join(PROMPTS_DIR, f"review_prompt_{slug}_{ct}.txt")
    if os.path.exists(path):
        return path
    fallback = os.path.join(PROMPTS_DIR, f"review_prompt_{slug}.txt")
    if os.path.exists(fallback):
        return fallback
    return None


def extract_final_markdown(response_text):
    match = re.search(r"```markdown\s*(.*?)```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*(#.+?)```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    h1_match = re.search(r"(^# .+)", response_text, re.MULTILINE)
    if h1_match:
        return response_text[h1_match.start():].strip()
    return response_text.strip()


def call_gemini_api(prompt_text):
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY 환경변수가 없어요.")
        sys.exit(1)

    url     = GEMINI_URL.format(api_key=GEMINI_API_KEY)
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        # Google Search 그라운딩: 실제 웹 검색으로 팩트체크.
        # Claude 웹검색과 달리 검색 결과가 입력 토큰에 통째로 얹히지 않아
        # 토큰 폭발이 없고, 그라운딩 요청 단위로만 과금된다.
        "tools": [{"google_search": {}}],
        "generationConfig": {
            "temperature":     0.3,   # 팩트체크는 낮은 온도로
            "maxOutputTokens": 8192,
        }
    }

    grounding_on = True
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            mode = "그라운딩 ON" if grounding_on else "그라운딩 OFF"
            print(f"  🤖 Gemini Review API 호출 중... (시도 {attempt}/{MAX_RETRIES}, {mode})")
            resp = requests.post(url, json=payload, timeout=180)

            if resp.status_code == 200:
                data       = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    print("  ⚠️ candidates 없음")
                    continue
                cand  = candidates[0]
                parts = cand.get("content", {}).get("parts", [])
                text  = "".join(p.get("text", "") for p in parts).strip()
                if text:
                    # 그라운딩 실제 수행 여부 로그
                    gm = cand.get("groundingMetadata", {})
                    queries = gm.get("webSearchQueries", [])
                    if queries:
                        print(f"  🔎 웹 검증 수행: {len(queries)}개 쿼리")
                    elif grounding_on:
                        print("  ℹ️  그라운딩 활성이나 검색 미수행 (지식 기반 판정)")
                    return text
                print("  ⚠️ 응답 텍스트 비어있음")

            elif resp.status_code == 400 and grounding_on:
                # 그라운딩 미지원/포맷 오류 → 그라운딩 없이 폴백
                print(f"  ⚠️ 400 오류 — 그라운딩 제거 후 재시도: {resp.text[:150]}")
                payload.pop("tools", None)
                grounding_on = False
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


def save_final(final_text, cluster_name, content_type):
    os.makedirs(FINAL_DIR, exist_ok=True)
    slug       = slugify(cluster_name)
    ct         = content_type.upper().strip()
    final_path = os.path.join(FINAL_DIR, f"{slug}_{ct}.md")
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(final_text)
    return final_path


INTRO_CONCLUSION_PROMPT = """You are a strict editorial quality checker and rewriter for Frontbuffer Editorial.

TASK: Check the intro and conclusion of the article below for boilerplate patterns.
If boilerplate is found, rewrite ONLY those sentences. Return the FULL article with fixes applied.
If no boilerplate is found, return the article UNCHANGED.

BOILERPLATE PATTERNS TO REJECT:

Intro (first 3 sentences):
❌ "Managing X requires balancing Y"
❌ "In an increasingly / rapidly / ever-changing world"
❌ "As technology continues to / evolves"
❌ "In today's fast-paced / modern era"
❌ "With the rise of"
❌ "Whether you are a [beginner/expert]"
❌ "If you've ever wondered" / "Have you ever"
❌ "This guide/article will help you understand / breaks down / covers"
❌ Any sentence that still makes sense if you replace the topic with a different one

Conclusion (last paragraph):
❌ "Maintaining a stable X environment is vital for keeping Y running smoothly"
❌ "Regularly doing X ensures Y continues to deliver"
❌ "We hope this guide has helped"
❌ "By following the steps above"
❌ "The choice is yours"
❌ "Staying informed is key"
❌ "In conclusion, [topic] is important / exciting"
❌ Any sentence that works if you swap the topic with something else

REQUIRED INSTEAD:
✅ Intro: Start with a specific fact, date, product name, or event directly tied to this article's topic.
   Pattern: "[Specific thing] happened / works this way. Here is what that means."
✅ Conclusion: End with a specific, actionable takeaway that references a detail from the article body.
   Must NOT be applicable to any other topic.

ARTICLE:
---
{article}
---

OUTPUT RULES:
- Return the COMPLETE article in markdown
- If you rewrote anything, add one line at the very top: [REWRITTEN: intro] or [REWRITTEN: conclusion] or [REWRITTEN: intro+conclusion]
- If nothing was changed, add one line at the very top: [NO CHANGE]
- No other commentary. Start directly with the tag line."""


def rewrite_intro_conclusion(final_text, cluster_name):
    """서론/결론 보일러플레이트 감지 + 재작성. 변경 없으면 원문 그대로 반환."""
    if not GEMINI_API_KEY:
        return final_text, "skipped"

    prompt = INTRO_CONCLUSION_PROMPT.format(article=final_text)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature":     0.4,
            "maxOutputTokens": 8192,
        }
    }
    url = GEMINI_URL.format(api_key=GEMINI_API_KEY)

    print(f"  ✍️  서론/결론 보일러플레이트 재검토 중...")
    try:
        resp = requests.post(url, json=payload, timeout=120)
        if resp.status_code != 200:
            print(f"  ⚠️  재검토 API 오류 ({resp.status_code}) — 원문 유지")
            return final_text, "error"

        parts = (resp.json()
                 .get("candidates", [{}])[0]
                 .get("content", {})
                 .get("parts", [{}]))
        raw = "".join(p.get("text", "") for p in parts).strip()
        if not raw:
            print(f"  ⚠️  재검토 응답 비어있음 — 원문 유지")
            return final_text, "error"

        # 첫 줄에서 태그 추출
        lines     = raw.splitlines()
        tag_line  = lines[0].strip() if lines else ""
        article   = "\n".join(lines[1:]).strip() if len(lines) > 1 else raw

        if "[NO CHANGE]" in tag_line:
            print(f"  ✅ 서론/결론 이상 없음 — 원문 유지")
            return final_text, "no_change"
        elif "[REWRITTEN:" in tag_line:
            what = tag_line.replace("[REWRITTEN:", "").replace("]", "").strip()
            print(f"  🔧 보일러플레이트 감지 → 재작성 완료 ({what})")
            return article, f"rewritten:{what}"
        else:
            # 태그 없이 본문만 온 경우 — 변경된 것으로 간주
            print(f"  🔧 재작성 완료 (태그 없음)")
            return raw, "rewritten"

    except Exception as e:
        print(f"  ⚠️  재검토 예외: {e} — 원문 유지")
        return final_text, "error"


def check_final_quality(final_text):
    word_count = len(final_text.split())
    errors     = []
    warnings   = []

    if word_count < 600:
        errors.append(f"단어 수 {word_count}개 — 600 미만")
    elif word_count < 800:
        warnings.append(f"단어 수 {word_count}개 — 800 미만")

    nv_count = len(re.findall(r"\[NEEDS VERIFICATION\]", final_text))
    if nv_count > 0:
        warnings.append(f"[NEEDS VERIFICATION] {nv_count}개 미해소")

    return {"ok": len(errors) == 0, "errors": errors,
            "warnings": warnings, "word_count": word_count}


def main():
    parser = argparse.ArgumentParser(description="Gemini Review API 팩트체크 + 최종본 생성")
    parser.add_argument("--cluster", required=True, help="클러스터명")
    parser.add_argument("--type",    required=True, help="content_type")
    args = parser.parse_args()

    cluster_name = args.cluster
    content_type = args.type.upper()

    print(f"\n{'='*60}")
    print(f"🔍 Gemini Review 팩트체크 + 최종본: {cluster_name} [{content_type}]")
    print(f"{'='*60}")
    print(f"  모델: {GEMINI_MODEL}")

    # 1. review_prompt 파일 찾기
    prompt_path = find_review_prompt(cluster_name, content_type)
    if not prompt_path:
        print(f"❌ review_prompt 파일 없음 — write.py review 먼저 실행하세요.")
        sys.exit(1)

    print(f"  📄 리뷰 프롬프트: {prompt_path}")
    prompt_text = open(prompt_path, encoding="utf-8").read()
    print(f"  📏 프롬프트 크기: {len(prompt_text.encode())/1024:.1f} KB")

    # 2. Gemini API 호출
    start         = time.time()
    response_text = call_gemini_api(prompt_text)
    elapsed       = time.time() - start

    if not response_text:
        print("❌ 최종본 생성 실패 — API 응답 없음")
        sys.exit(1)

    print(f"  ✅ API 응답 완료 ({elapsed:.1f}초)")

    # 3. 최종본 추출
    final_text = extract_final_markdown(response_text)
    print(f"  📝 최종본 추출 완료 ({len(final_text.split())}단어)")

    # 4. 서론/결론 보일러플레이트 재검토 + 재작성
    final_text, rewrite_status = rewrite_intro_conclusion(final_text, cluster_name)
    time.sleep(2)  # API rate limit 여유

    # 5. 품질 체크
    quality = check_final_quality(final_text)
    print(f"  📊 단어 수: {quality['word_count']}개")
    for w in quality["warnings"]:
        print(f"  ⚠️  {w}")
    for e in quality["errors"]:
        print(f"  ❌ {e}")

    if not quality["ok"]:
        print("⚠️  품질 경고 있음 — 저장은 진행 (수동 확인 필요)")

    # 5. 최종본 저장
    final_path = save_final(final_text, cluster_name, content_type)
    print(f"  💾 최종본 저장: {final_path}")

    # 6. 판정 리포트 저장
    slug        = slugify(cluster_name)
    ct          = content_type.upper().strip()
    report_path = os.path.join(FINAL_DIR, f"review_report_{slug}_{ct}.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(response_text)
    print(f"  📋 판정 리포트: {report_path}")

    # 7. 결과 JSON
    result = {
        "ok":             quality["ok"],
        "cluster":        cluster_name,
        "content_type":   content_type,
        "final_path":     final_path,
        "report_path":    report_path,
        "word_count":     quality["word_count"],
        "warnings":       quality["warnings"],
        "errors":         quality["errors"],
        "rewrite_status": rewrite_status,
        "elapsed":        round(elapsed, 1),
        "timestamp":      datetime.now(timezone.utc).isoformat(),
    }
    print(f"\n✅ 완료: {json.dumps(result, ensure_ascii=False)}")
    print(f"""
다음 단계:
  python write.py done "{cluster_name}" --type {content_type}
""")


if __name__ == "__main__":
    main()
