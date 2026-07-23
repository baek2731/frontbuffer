# =====================================================================
# 🔍 품질 체크 (quality_check.py)
# =====================================================================
# 역할: Step 3 완료 후 final/ 의 신규 글을 평가
#       규칙 기반 체크 (100% 정확) + Gemini YES/NO 체크 (패턴 감지)
#
# 사용법:
#   python quality_check.py                   → final/ 전체 체크
#   python quality_check.py --files a.md,b.md → 특정 파일만 체크
#   python quality_check.py --json            → JSON 출력 (Actions 파싱용)
#
# 출력:
#   quality_report.json  → Discord 알림용 (notify.py가 읽음)
#
# 체크 항목:
#   [규칙 기반 — 코드]
#   R1. [INTERNAL LINK] 플레이스홀더 잔존
#   R2. [NEEDS VERIFICATION] 태그 잔존
#   R3. 단어수 800 미달
#   R4. H1 존재 여부
#
#   [Gemini YES/NO — 서론/결론만 발췌해서 판단]
#   G1. 금지 서론 오프너 패턴
#   G2. 1인칭 사용 ("I", "my", "I've")
#   G3. 금지 결론 패턴
#   G4. 주제 교체해도 말이 되는 결론 (generic boilerplate)
# =====================================================================

import os
import re
import sys
import json
import time
import argparse
import requests
from pathlib import Path

FINAL_DIR   = "research_data/write/final"
REPORT_FILE = "research_data/write/quality_report.json"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL     = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

REPO          = os.environ.get("GITHUB_REPOSITORY", "baek2731/frontbuffer")
GITHUB_BRANCH = "main"

# ── GitHub 파일 직링크 생성 ──────────────────────────────────────────

def github_link(filepath: str) -> str:
    rel = filepath.replace("\\", "/")
    return f"https://github.com/{REPO}/blob/{GITHUB_BRANCH}/{rel}"


# ── 규칙 기반 체크 ──────────────────────────────────────────────────

RULE_CHECKS = [
    {
        "id":      "R1",
        "label":   "[INTERNAL LINK] 플레이스홀더 잔존",
        "pattern": r"\[INTERNAL LINK[^\]]*\]",
    },
    {
        "id":      "R2",
        "label":   "[NEEDS VERIFICATION] 태그 잔존",
        "pattern": r"\[NEEDS VERIFICATION[^\]]*\]",
    },
    {
        "id":      "R4",
        "label":   "H1 제목 없음",
        "pattern": None,   # 특수 처리
    },
]

def run_rule_checks(text: str) -> list:
    """규칙 기반 체크 — 100% 정확."""
    issues = []

    for chk in RULE_CHECKS:
        if chk["pattern"] is None:
            # R4: H1 존재 여부
            if not re.search(r'^# .+', text, re.MULTILINE):
                issues.append({"id": chk["id"], "label": chk["label"]})
        else:
            if re.search(chk["pattern"], text):
                issues.append({"id": chk["id"], "label": chk["label"]})

    # R3: 단어수 체크
    word_count = len(re.findall(r'\b\w+\b', text))
    if word_count < 800:
        issues.append({
            "id":    "R3",
            "label": f"단어수 미달 ({word_count}단어 / 최소 800)",
        })

    return issues


# ── Gemini YES/NO 체크 ───────────────────────────────────────────────

GEMINI_PROMPT_TEMPLATE = """You are a strict editorial quality checker.
Read ONLY the excerpt below (intro + conclusion of an article).
Answer each question with YES or NO only. One answer per line. No explanation.

Q1. Does the intro contain any of these forbidden patterns?
    - "In an increasingly / rapidly / ever-changing world"
    - "As technology continues to / evolves"
    - "In today's fast-paced / modern era"
    - "With the rise of"
    - "Whether you are a [beginner/expert]"
    - "If you've ever wondered" / "Have you ever"
    Answer YES if ANY of these appear (even paraphrased).

Q2. Does the intro use first-person singular?
    ("I", "my", "me", "I've", "In my experience", "I found")
    Answer YES if ANY appear.

Q3. Does the conclusion contain any of these forbidden patterns?
    - "we hope this guide / article has helped"
    - "by following the steps / tips above"
    - "the choice is yours"
    - "staying informed is key"
    - "In conclusion, [topic] is important / exciting"
    - "As [technology] continues to evolve"
    Answer YES if ANY appear (even paraphrased).

Q4. Would the conclusion still make sense if you replaced the article topic
    with a completely different topic (e.g. swap "Chrome extensions" with
    "cooking recipes")? Answer YES if the conclusion is that generic.

EXCERPT:
---
{excerpt}
---

Answer format (4 lines, exactly):
Q1: YES or NO
Q2: YES or NO
Q3: YES or NO
Q4: YES or NO"""


def extract_excerpt(text: str) -> str:
    """서론 첫 3문장 + 결론 마지막 3문장 추출."""
    # front matter 제거
    body = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    # H1 제거
    body = re.sub(r'^# .+\n', '', body, flags=re.MULTILINE)
    # [SOURCES USED] 이하 제거
    body = re.sub(r'\[SOURCES USED.*', '', body, flags=re.DOTALL)

    # 문장 단위 분리 (마침표/느낌표/물음표 기준)
    sentences = re.split(r'(?<=[.!?])\s+', body.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    intro      = " ".join(sentences[:3])
    conclusion = " ".join(sentences[-3:]) if len(sentences) >= 3 else intro

    return f"[INTRO]\n{intro}\n\n[CONCLUSION]\n{conclusion}"


def run_gemini_checks(excerpt: str) -> list:
    """Gemini에 YES/NO 4문항 질의."""
    if not GEMINI_API_KEY:
        print("  ⚠️  GEMINI_API_KEY 없음 — Gemini 체크 스킵")
        return []

    prompt = GEMINI_PROMPT_TEMPLATE.format(excerpt=excerpt)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 60},
    }

    try:
        resp = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=20,
        )
        if resp.status_code != 200:
            print(f"  ⚠️  Gemini API 오류 ({resp.status_code}) — 스킵")
            return []

        raw = (resp.json()
               .get("candidates", [{}])[0]
               .get("content", {})
               .get("parts", [{}])[0]
               .get("text", ""))
    except Exception as e:
        print(f"  ⚠️  Gemini 요청 실패: {e} — 스킵")
        return []

    # 파싱
    label_map = {
        "Q1": "서론 금지 오프너 패턴 감지",
        "Q2": "서론 1인칭 사용 감지",
        "Q3": "결론 금지 패턴 감지",
        "Q4": "결론 보일러플레이트 (주제 교체해도 통용됨)",
    }
    issues = []
    for line in raw.strip().splitlines():
        m = re.match(r'(Q\d):\s*(YES|NO)', line.strip(), re.IGNORECASE)
        if m:
            qid, ans = m.group(1), m.group(2).upper()
            if ans == "YES":
                issues.append({
                    "id":    f"G{qid[1]}",
                    "label": label_map.get(qid, qid),
                })
    return issues


# ── 파일 1개 체크 ───────────────────────────────────────────────────

def check_file(filepath: str) -> dict:
    """파일 1개 전체 체크. 결과 dict 반환."""
    path = Path(filepath)
    print(f"\n  📄 {path.name}")

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"file": str(path), "error": str(e), "issues": [], "ok": False}

    # 규칙 기반
    rule_issues = run_rule_checks(text)

    # Gemini YES/NO
    excerpt      = extract_excerpt(text)
    gemini_issues = run_gemini_checks(excerpt)
    time.sleep(1)   # API rate limit 여유

    all_issues = rule_issues + gemini_issues
    ok         = len(all_issues) == 0

    # 로그 출력
    if ok:
        print("    ✅ 이상 없음")
    else:
        for iss in all_issues:
            print(f"    ❌ [{iss['id']}] {iss['label']}")

    return {
        "file":   str(path),
        "name":   path.stem,
        "link":   github_link(str(path)),
        "issues": all_issues,
        "ok":     ok,
    }


# ── 메인 ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="품질 체크")
    parser.add_argument("--files", default="",
                        help="체크할 파일 목록 (쉼표 구분). 미지정 시 final/ 전체")
    parser.add_argument("--json", action="store_true",
                        help="JSON 출력 (Actions 파싱용)")
    args = parser.parse_args()

    # 체크 대상 파일 결정
    if args.files:
        targets = [f.strip() for f in args.files.split(",") if f.strip()]
    else:
        targets = sorted(
            str(p) for p in Path(FINAL_DIR).glob("*.md")
            if not p.name.startswith("review_report_")
        )

    if not targets:
        print("ℹ️  체크할 파일 없음")
        report = {"total": 0, "ok": 0, "issues": [], "results": []}
        Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
        Path(REPORT_FILE).write_text(json.dumps(report, ensure_ascii=False, indent=2))
        if args.json:
            print(json.dumps(report))
        return

    print(f"\n🔍 품질 체크 시작 — {len(targets)}개 파일")
    print("=" * 60)

    results    = []
    issue_list = []   # Discord 알림용 요약

    for fp in targets:
        result = check_file(fp)
        results.append(result)
        if not result.get("ok") and not result.get("error"):
            issue_list.append({
                "name":   result["name"],
                "link":   result["link"],
                "issues": result["issues"],
            })

    ok_count    = sum(1 for r in results if r.get("ok"))
    issue_count = len(issue_list)

    print("\n" + "=" * 60)
    print(f"🏁 완료: 이상 없음 {ok_count}편 / 확인 필요 {issue_count}편")

    report = {
        "total":       len(results),
        "ok":          ok_count,
        "issue_count": issue_count,
        "issue_files": issue_list,
        "results":     results,
    }

    Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
    Path(REPORT_FILE).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"📝 리포트 저장: {REPORT_FILE}")

    if args.json:
        print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
