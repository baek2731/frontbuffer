# =====================================================================
# 🔎 Step 5 — 주간 품질 감사 (step5_audit.py)
# =====================================================================
# 역할: _posts/ + final/ + published/를 검사해서
#       자동 수정 가능한 것은 고치고,
#       수동 확인 필요한 것은 audit_report.md에 기록.
#
# 사용법:
#   python step5_audit.py [--dry-run]
#
# 체크 항목:
#   ✅ [INTERNAL LINK] / [AFFILIATE LINK] 플레이스홀더 잔존 (자동 제거)
#   ✅ [NEEDS VERIFICATION] 미해소 (수동 확인)
#   ✅ 단어 수 600 미만 (수동 확인)
#   ✅ front matter 필수 필드 누락 (수동 확인)
#   ✅ published/ ↔ _posts/ 불일치 (자동 동기화)
#   ✅ 클러스터별 HUB-스포크 연결 완성도 (수동 확인)
#   ✅ final/ 스택 잔량 경고 (3편 미만)
#   ✅ 외부 링크 404 검사 (수동 확인, 최대 30개)
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

POSTS_DIR     = "_posts"
FINAL_DIR     = "research_data/write/final"
PUBLISHED_DIR = "research_data/write/published"
PIPELINE_FILE = "content_pipeline.json"
REPORT_FILE   = "research_data/write/audit_report.md"

REQUIRED_FRONT_MATTER = ["layout", "title", "date", "categories", "tags", "excerpt"]


# ── 유틸 ──────────────────────────────────────────────────────────────

def load_pipeline():
    if not os.path.exists(PIPELINE_FILE):
        return {}
    with open(PIPELINE_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_posts():
    """_posts/ 아래 .md 파일 목록 반환."""
    return sorted(Path(POSTS_DIR).glob("*.md")) if Path(POSTS_DIR).exists() else []


def get_final_stack():
    """final/ 실제 발행 대기 파일 수."""
    if not Path(FINAL_DIR).exists():
        return 0
    return len([f for f in Path(FINAL_DIR).glob("*.md")
                if not f.name.startswith("review_report_")])


def parse_front_matter(text):
    """--- ... --- 블록에서 키 목록 반환."""
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    keys = {}
    for line in match.group(1).splitlines():
        m = re.match(r"^(\w+)\s*:", line)
        if m:
            keys[m.group(1)] = True
    return keys


def count_words(text):
    """front matter 제외 본문 단어 수."""
    body = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)
    return len(body.split())


def check_link_404(url: str, timeout: int = 8) -> bool:
    """URL이 404인지 확인. True = 404(문제), False = 정상."""
    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0"})
        return resp.status_code == 404
    except Exception:
        return False   # 접속 오류는 404로 처리하지 않음 (과탐지 방지)


# ── 검사 함수들 ───────────────────────────────────────────────────────

def check_placeholders(posts, dry_run: bool):
    """플레이스홀더 잔존 검사 + 자동 제거."""
    auto_fixed = []
    manual_needed = []

    PLACEHOLDER_RE = [
        (r'\[INTERNAL LINK:[^\]]*\](?!\()',  ''),
        (r'\[AFFILIATE LINK:[^\]]*\](?!\()', ''),
        (r'\[NEEDS VERIFICATION\]',           None),   # None = 수동 확인
        (r'\[Source:[^\]]*\](?!\(',           ''),
    ]

    for post in posts:
        text = post.read_text(encoding="utf-8")
        modified = text
        needs_manual = []

        for pattern, replacement in PLACEHOLDER_RE:
            matches = re.findall(pattern, text)
            if not matches:
                continue
            if replacement is None:
                needs_manual.append(f"`[NEEDS VERIFICATION]` {len(matches)}개")
            else:
                modified = re.sub(pattern, replacement, modified)

        if modified != text:
            if not dry_run:
                post.write_text(modified, encoding="utf-8")
            auto_fixed.append(f"{post.name} — 플레이스홀더 {len(re.findall(chr(91), text))}개 제거")

        if needs_manual:
            manual_needed.append(f"{post.name}: " + ", ".join(needs_manual))

    return auto_fixed, manual_needed


def check_word_count(posts):
    """단어 수 600 미만 글 목록."""
    low = []
    for post in posts:
        text  = post.read_text(encoding="utf-8")
        words = count_words(text)
        if words < 600:
            low.append(f"{post.name} — {words}단어")
    return low


def check_front_matter(posts):
    """필수 front matter 필드 누락."""
    issues = []
    for post in posts:
        text   = post.read_text(encoding="utf-8")
        keys   = parse_front_matter(text)
        missing = [k for k in REQUIRED_FRONT_MATTER if k not in keys]
        if missing:
            issues.append(f"{post.name} — 누락 필드: {', '.join(missing)}")
    return issues


def check_published_sync(posts, dry_run: bool):
    """published/ ↔ _posts/ 동기화 검사."""
    auto_fixed = []
    manual_needed = []

    pub_dir = Path(PUBLISHED_DIR)
    if not pub_dir.exists():
        return auto_fixed, manual_needed

    post_names = {p.name for p in posts}
    pub_names  = {p.name for p in pub_dir.glob("*.md")}

    # _posts/에 없는데 published/에 있는 경우 (역동기화 — 수동 확인)
    orphan_pub = pub_names - post_names
    for name in sorted(orphan_pub):
        manual_needed.append(f"published/{name} — _posts/에 없음 (발행 누락?)")

    # _posts/에 있는데 published/에 없는 경우 → 자동 복사
    missing_pub = post_names - pub_names
    for name in sorted(missing_pub):
        src = Path(POSTS_DIR) / name
        dst = pub_dir / name
        if not dry_run:
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        auto_fixed.append(f"published/{name} 동기화 복사")

    # 내용 불일치 검사
    for name in post_names & pub_names:
        post_text = (Path(POSTS_DIR) / name).read_text(encoding="utf-8")
        pub_text  = (pub_dir / name).read_text(encoding="utf-8")
        if post_text != pub_text:
            if not dry_run:
                (pub_dir / name).write_text(post_text, encoding="utf-8")
            auto_fixed.append(f"published/{name} 내용 불일치 → _posts/ 기준으로 덮어씀")

    return auto_fixed, manual_needed


def check_hub_spoke(pipeline):
    """클러스터별 HUB-스포크 연결 완성도."""
    issues = []
    published = pipeline.get("published", [])

    # 클러스터별 발행된 타입 분류
    clusters = {}
    for p in published:
        name = p.get("cluster_name", "")
        ct   = p.get("content_type", "").upper()
        if name not in clusters:
            clusters[name] = {"hub": False, "spokes": []}
        if ct == "HUB":
            clusters[name]["hub"] = True
        else:
            clusters[name]["spokes"].append(ct)

    for cluster, info in clusters.items():
        spoke_count = len(info["spokes"])
        if spoke_count >= 2 and not info["hub"]:
            issues.append(f"**{cluster}** — 스포크 {spoke_count}개 발행됐으나 HUB 없음")
        if info["hub"] and spoke_count < 2:
            issues.append(f"**{cluster}** — HUB 발행됐으나 스포크 {spoke_count}개만 있음")

    return issues


def check_links_404(posts, max_links: int = 30):
    """외부 링크 404 검사 (최대 max_links개, 시간 절약)."""
    issues = []
    checked = 0

    for post in posts:
        if checked >= max_links:
            break
        text  = post.read_text(encoding="utf-8")
        links = re.findall(r'\[(?:[^\]]+)\]\((https?://[^\)]+)\)', text)
        for url in links:
            if checked >= max_links:
                break
            checked += 1
            if check_link_404(url):
                issues.append(f"{post.name}: [{url}]")
            time.sleep(0.3)   # 과부하 방지

    return issues


# ── 리포트 생성 ──────────────────────────────────────────────────────

def write_report(auto_fixed, manual_items, stack, dry_run: bool):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Frontbuffer 주간 품질 감사 리포트",
        f"생성: {now}  |  dry-run: {dry_run}",
        "",
        f"## 요약",
        f"- 자동 수정: **{sum(len(v) for v in auto_fixed.values())}건**",
        f"- 수동 확인 필요: **{sum(len(v) for v in manual_items.values())}건**",
        f"- final/ 스택 잔량: **{stack}편**",
        "",
    ]

    for section, items in auto_fixed.items():
        if items:
            lines.append(f"## ✅ 자동 수정 — {section}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    for section, items in manual_items.items():
        if items:
            lines.append(f"## ⚠️ 수동 확인 필요 — {section}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    if stack < 3:
        lines += [
            "## 🚨 스택 잔량 부족",
            f"final/ 잔량 {stack}편 — Step 2/3를 수동 실행해 보충하세요.",
            "",
        ]

    if not dry_run:
        os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
        Path(REPORT_FILE).write_text("\n".join(lines), encoding="utf-8")
        print(f"📋 리포트 저장: {REPORT_FILE}")
    else:
        print("\n".join(lines))


# ── 메인 ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Frontbuffer 주간 품질 감사")
    parser.add_argument("--dry-run", action="store_true",
                        help="변경사항을 실제로 쓰지 않고 리포트만 출력")
    parser.add_argument("--skip-links", action="store_true",
                        help="외부 링크 404 검사 건너뜀 (빠른 실행)")
    args = parser.parse_args()

    dry_run    = args.dry_run
    skip_links = args.skip_links

    print(f"\n{'='*60}")
    print(f"🔎 Frontbuffer 주간 품질 감사 {'[DRY-RUN]' if dry_run else ''}")
    print(f"{'='*60}")

    posts    = get_posts()
    stack    = get_final_stack()
    pipeline = load_pipeline()

    print(f"  _posts/ : {len(posts)}편")
    print(f"  final/  : {stack}편 (발행 대기)")

    auto_fixed   = {}
    manual_items = {}

    # ── 1. 플레이스홀더 ──────────────────────────────────────────────
    print("\n[1/6] 플레이스홀더 검사...")
    fixed, manual = check_placeholders(posts, dry_run)
    auto_fixed["플레이스홀더 제거"]   = fixed
    manual_items["NEEDS VERIFICATION"] = manual
    print(f"  자동 수정 {len(fixed)}건 / 수동 확인 {len(manual)}건")

    # ── 2. 단어 수 ────────────────────────────────────────────────────
    print("\n[2/6] 단어 수 검사 (600 미만)...")
    low = check_word_count(posts)
    manual_items["단어 수 미달"] = low
    print(f"  해당 글: {len(low)}건")

    # ── 3. front matter ───────────────────────────────────────────────
    print("\n[3/6] front matter 검사...")
    fm_issues = check_front_matter(posts)
    manual_items["front matter 누락"] = fm_issues
    print(f"  이슈: {len(fm_issues)}건")

    # ── 4. published/ 동기화 ─────────────────────────────────────────
    print("\n[4/6] published/ 동기화 검사...")
    fixed, manual = check_published_sync(posts, dry_run)
    auto_fixed["published/ 동기화"]   = fixed
    manual_items["published/ 불일치"] = manual
    print(f"  자동 수정 {len(fixed)}건 / 수동 확인 {len(manual)}건")

    # ── 5. HUB-스포크 ─────────────────────────────────────────────────
    print("\n[5/6] HUB-스포크 연결 검사...")
    hub_issues = check_hub_spoke(pipeline)
    manual_items["HUB-스포크 연결"] = hub_issues
    print(f"  이슈: {len(hub_issues)}건")

    # ── 6. 외부 링크 404 ─────────────────────────────────────────────
    if skip_links:
        print("\n[6/6] 외부 링크 검사 — 스킵")
        manual_items["외부 링크 404"] = []
    else:
        print("\n[6/6] 외부 링크 404 검사 (최대 30개)...")
        link_issues = check_links_404(posts)
        manual_items["외부 링크 404"] = link_issues
        print(f"  404 링크: {len(link_issues)}건")

    # ── 집계 ─────────────────────────────────────────────────────────
    total_auto   = sum(len(v) for v in auto_fixed.values())
    total_manual = sum(len(v) for v in manual_items.values())

    print(f"\n{'='*60}")
    print(f"📊 결과 요약")
    print(f"  자동 수정    : {total_auto}건")
    print(f"  수동 확인    : {total_manual}건")
    print(f"  스택 잔량    : {stack}편")
    print(f"{'='*60}")

    # ── 리포트 저장 ──────────────────────────────────────────────────
    write_report(auto_fixed, manual_items, stack, dry_run)

    # ── GitHub ENV 출력 (Actions 알림용) ─────────────────────────────
    github_env = os.environ.get("GITHUB_ENV", "")
    if github_env:
        with open(github_env, "a") as f:
            f.write(f"AUDIT_AUTO={total_auto}\n")
            f.write(f"AUDIT_MANUAL={total_manual}\n")
            f.write(f"AUDIT_STACK={stack}\n")

    if total_manual > 0:
        print(f"\n⚠️  수동 확인 항목 {total_manual}건 — audit_report.md 확인")

    if stack < 3:
        print(f"\n🚨 스택 잔량 {stack}편 — 보충 필요!")


if __name__ == "__main__":
    main()
