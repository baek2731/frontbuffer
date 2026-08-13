#!/usr/bin/env python3
"""
adsense_audit.py — 애드센스 신청 전 _posts/ 전체 품질 검사
"""
import os
import re
import json
from pathlib import Path

POSTS_DIR = "_posts"

# ── 검사 패턴 ──────────────────────────────────────────────────────

# AI 냄새 서론 패턴
AI_INTRO_PATTERNS = [
    r"has emerged as a significant",
    r"in an increasingly digital world",
    r"in today.s (fast-paced|rapidly evolving|ever-changing)",
    r"as technology continues to",
    r"with the rise of",
    r"this article delves into",
    r"we will explore how",
    r"offering a compelling blend",
    r"marks a significant evolution",
    r"represents a pivotal moment",
    r"directly addressing persistent challenges",
    r"it.s worth noting that",
    r"this guide will help you unlock",
]

# AI 냄새 결론 패턴
AI_CONCLUSION_PATTERNS = [
    r"solidify.+position at the forefront",
    r"underscores.+commitment to continuous innovation",
    r"staying informed is key",
    r"the choice is yours",
    r"we hope this guide has helped",
    r"by following the steps above",
    r"as.+continues to evolve",
    r"minimizing downtime and maximizing",
    r"ensuring you can confidently",
]

# 발행 불가 패턴
BLOCK_PATTERNS = [
    (r"\[cite:\s*\d+", "Gemini cite 번호 잔존"),
    (r"\[INTERNAL LINK:", "미처리 내부링크"),
    (r"판정 요약", "한국어 판정 메모"),
    (r"\[NEEDS VERIFICATION\]", "검증 미완료 태그"),
]

# 나쁜 출처 패턴
BAD_SOURCES = [
    r"youtube\.com",
    r"youtu\.be",
    r"reddit\.com",
    r"ebay\.com",
    r"amazon\.com",
]

# 숫자 태그 패턴
NUMERIC_TAG_PATTERN = r'"(\d+)"'

def parse_frontmatter(content):
    """frontmatter 파싱."""
    fm = {}
    if not content.startswith("---"):
        return fm, content
    end = content.find("---", 3)
    if end == -1:
        return fm, content
    fm_text = content[3:end]
    body = content[end+3:]

    for line in fm_text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip("'\"")
    return fm, body

def check_word_count(body):
    """단어 수 계산."""
    words = re.findall(r'\b\w+\b', body)
    return len(words)

def audit_post(filepath):
    """단일 파일 검사."""
    content = Path(filepath).read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)
    issues = []
    warnings = []

    # 1. 발행 불가 패턴
    for pattern, desc in BLOCK_PATTERNS:
        if re.search(pattern, content):
            issues.append(f"🔴 발행 불가: {desc}")

    # 2. 숫자 태그
    tags_line = fm.get("tags", "")
    numeric_tags = re.findall(NUMERIC_TAG_PATTERN, tags_line)
    if numeric_tags:
        warnings.append(f"🟡 숫자 태그 존재: {numeric_tags}")

    # 3. header 이미지 없음
    if "header:" not in content:
        warnings.append("🟡 header 이미지 없음")

    # 4. AI 냄새 서론 (첫 200단어)
    first_para = " ".join(body.split()[:200]).lower()
    for pat in AI_INTRO_PATTERNS:
        if re.search(pat, first_para):
            warnings.append(f"🟡 AI 냄새 서론: '{pat}'")
            break

    # 5. AI 냄새 결론 (마지막 200단어)
    last_para = " ".join(body.split()[-200:]).lower()
    for pat in AI_CONCLUSION_PATTERNS:
        if re.search(pat, last_para):
            warnings.append(f"🟡 AI 냄새 결론: '{pat}'")
            break

    # 6. 나쁜 출처
    for pat in BAD_SOURCES:
        if re.search(pat, body, re.IGNORECASE):
            warnings.append(f"🟡 나쁜 출처: {pat}")

    # 7. 단어 수
    word_count = check_word_count(body)
    if word_count < 400:
        warnings.append(f"🟡 분량 부족: {word_count}단어 (권장 400+)")

    # 8. excerpt 없음
    if not fm.get("excerpt"):
        warnings.append("🟡 excerpt 없음")

    # 9. permalink에 _hub 포함
    permalink = fm.get("permalink", "")
    if "_hub" in permalink:
        warnings.append(f"🟡 permalink에 _hub 포함: {permalink}")

    return {
        "file": Path(filepath).name,
        "title": fm.get("title", "N/A")[:50],
        "issues": issues,
        "warnings": warnings,
        "word_count": word_count,
    }

def main():
    posts = sorted(Path(POSTS_DIR).glob("*.md"))
    if not posts:
        print(f"❌ {POSTS_DIR}/ 폴더에 .md 파일 없음")
        return

    results = []
    for post in posts:
        result = audit_post(post)
        results.append(result)

    # 리포트 출력
    print("=" * 70)
    print(f"📋 애드센스 신청 전 품질 검사 리포트 — {len(results)}편")
    print("=" * 70)

    critical = [r for r in results if r["issues"]]
    warned = [r for r in results if r["warnings"] and not r["issues"]]
    clean = [r for r in results if not r["issues"] and not r["warnings"]]

    print(f"\n🔴 즉시 수정 필요: {len(critical)}편")
    print(f"🟡 검토 필요: {len(warned)}편")
    print(f"✅ 이상 없음: {len(clean)}편")

    if critical:
        print("\n" + "─" * 70)
        print("🔴 즉시 수정 필요")
        print("─" * 70)
        for r in critical:
            print(f"\n📄 {r['file']}")
            print(f"   제목: {r['title']}")
            for issue in r["issues"]:
                print(f"   {issue}")

    if warned:
        print("\n" + "─" * 70)
        print("🟡 검토 필요")
        print("─" * 70)
        for r in warned:
            print(f"\n📄 {r['file']}")
            print(f"   제목: {r['title']} ({r['word_count']}단어)")
            for w in r["warnings"]:
                print(f"   {w}")

    if clean:
        print("\n" + "─" * 70)
        print("✅ 이상 없음")
        print("─" * 70)
        for r in clean:
            print(f"   ✅ {r['file']} ({r['word_count']}단어)")

    # JSON 리포트 저장
    with open("adsense_audit_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n📊 상세 리포트 저장: adsense_audit_report.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
