# =====================================================================
# 📤 발행 스크립트 (publish_one.py) — Step 4에서 호출
# =====================================================================
# 역할: final/에서 가장 오래된 파일 1개를 꺼내서 _posts/에 발행
#
# 사용법:
#   python publish_one.py
#
# 동작:
#   1. final/에서 FIFO로 1개 선택 (HUB는 스포크 2개 이상 발행 후)
#   2. 플레이스홀더 제거 ([INTERNAL LINK: ...] 등)
#   3. front matter 생성 (오늘 날짜, 랜덤 분)
#   4. _posts/YYYY-MM-DD-{slug}_{type}.md 저장
#   5. write.py done 호출 (pipeline 기록)
#   6. final/ 파일 삭제 (중복 발행 방지)
# =====================================================================

import os
import re
import sys
import json
import random
import subprocess
from pathlib import Path
from datetime import datetime, timezone

FINAL_DIR     = "research_data/write/final"
PUBLISHED_DIR = "research_data/write/published"
POSTS_DIR     = "_posts"
PIPELINE_FILE = "content_pipeline.json"
POSTS_FILE    = "posts.json"


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def load_pipeline():
    with open(PIPELINE_FILE, encoding="utf-8") as f:
        return json.load(f)


def hub_ready(pipeline, cluster_name):
    """HUB 글은 해당 클러스터 스포크 2개 이상 발행 후에만 발행."""
    published = pipeline.get("published", [])
    spokes = [p for p in published
              if p.get("cluster_name") == cluster_name
              and p.get("content_type", "").upper() != "HUB"]
    return len(spokes) >= 2


def main():
    pipeline = load_pipeline()

    # ── final/ 파일 목록 (수정 시간 오름차순 FIFO) ─────────────────
    final_files = sorted(
        [f for f in Path(FINAL_DIR).glob("*.md")
         if not f.name.startswith("review_report_")],
        key=lambda f: f.stat().st_mtime
    )

    if not final_files:
        print("ℹ️  발행할 파일 없음 — 종료")
        sys.exit(0)

    # ── 발행 대상 선택 ─────────────────────────────────────────────
    target = None
    target_slug = None
    target_ct   = None
    skipped_hubs = []

    for f in final_files:
        stem  = f.stem
        parts = stem.rsplit("_", 1)
        if len(parts) != 2:
            continue
        slug, ct = parts[0], parts[1].upper()

        # 이미 발행된 파일 스킵
        already = any(
            slugify(p.get("cluster_name", "")) == slug
            and p.get("content_type", "").upper() == ct
            for p in pipeline.get("published", [])
        )
        if already:
            print(f"  ⏭️  이미 발행됨 — 스킵: {f.name}")
            continue

        # HUB 조건 체크
        if ct == "HUB":
            cluster_name = None
            for week_sels in pipeline.get("weekly_selections", {}).values():
                for sel in week_sels:
                    if (slugify(sel.get("cluster_name", "")) == slug
                            and sel.get("content_type", "").upper() == "HUB"):
                        cluster_name = sel.get("cluster_name")
                        break
                if cluster_name:
                    break

            if cluster_name and not hub_ready(pipeline, cluster_name):
                skipped_hubs.append(f.name)
                print(f"  ⏳ HUB 보류 (스포크 2개 미만): {f.name}")
                continue

        target      = f
        target_slug = slug
        target_ct   = ct
        break

    if not target:
        if skipped_hubs:
            print(f"ℹ️  발행 가능한 파일 없음 (HUB 보류: {len(skipped_hubs)}개)")
        else:
            print("ℹ️  발행할 파일 없음 — 종료")
        sys.exit(0)

    print(f"\n📤 발행 대상: {target.name}")

    # ── 본문 읽기 ──────────────────────────────────────────────────
    content = target.read_text(encoding="utf-8")

    # ── H1에서 제목 추출 ───────────────────────────────────────────
    title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    title = (title_match.group(1).strip()
             if title_match else target_slug.replace("-", " ").title())

    # ── 플레이스홀더 제거 ──────────────────────────────────────────
    content = re.sub(r'\[INTERNAL LINK:[^\]]*\]', '', content)
    content = re.sub(r'\[AFFILIATE LINK:[^\]]*\]', '', content)
    content = re.sub(r'\[NEEDS VERIFICATION\]', '', content)
    content = re.sub(r'\[Source:[^\]]*\]', '', content)

    # ── 날짜 설정 (UTC 14시 랜덤 분) ──────────────────────────────
    now       = datetime.now(timezone.utc)
    minute    = random.randint(0, 59)
    date_str  = now.strftime("%Y-%m-%d")
    dt_str    = f"{date_str} 14:{minute:02d}:00 +0000"

    # ── 카테고리 자동 분류 ─────────────────────────────────────────
    gaming_keys = ["steam", "game", "gaming", "xbox", "playstation",
                   "nintendo", "fallout", "portable", "handheld", "deck"]
    cat = "gaming" if any(k in target_slug for k in gaming_keys) else "tech"

    # ── 태그 생성 ──────────────────────────────────────────────────
    slug_words = target_slug.replace("-", " ").split()
    tags = list(dict.fromkeys([target_ct.lower()] + slug_words[:4]))[:6]
    tags_str = ", ".join(f'"{t}"' for t in tags)

    # ── excerpt 생성 ───────────────────────────────────────────────
    body_lines = [l for l in content.splitlines()
                  if l.strip()
                  and not l.startswith("#")
                  and not l.startswith("---")
                  and not l.startswith("[SOURCES")]
    excerpt = ""
    if body_lines:
        raw = body_lines[0]
        excerpt = (raw[:150].rsplit(" ", 1)[0] + "…"
                   if len(raw) > 150 else raw)

    yaml_title   = title.replace("'", "''")
    yaml_excerpt = excerpt.replace("'", "''")

    # ── front matter ───────────────────────────────────────────────
    front_matter = (
        f"---\n"
        f"layout: single\n"
        f"title: '{yaml_title}'\n"
        f"date: {dt_str}\n"
        f"categories: [{cat}]\n"
        f"tags: [{tags_str}]\n"
        f"excerpt: '{yaml_excerpt}'\n"
        f"author_profile: false\n"
        f"read_time: true\n"
        f"share: true\n"
        f"---\n\n"
    )

    # ── H1 + 소스 헤더 제거 ────────────────────────────────────────
    body = re.sub(r'^# .+\n', '', content, count=1, flags=re.MULTILINE)
    body = re.sub(r'^\[SOURCES USED:.*\]\n?', '', body, flags=re.MULTILINE)
    body = re.sub(r'^\[DISCARDED:.*\]\n?', '', body, flags=re.MULTILINE)

    final_content = front_matter + body.lstrip()

    # ── _posts/ 저장 ───────────────────────────────────────────────
    os.makedirs(POSTS_DIR, exist_ok=True)
    post_filename = f"{date_str}-{target_slug}_{target_ct.lower()}.md"
    post_path     = os.path.join(POSTS_DIR, post_filename)
    Path(post_path).write_text(final_content, encoding="utf-8")
    print(f"  📝 _posts/ 저장: {post_filename}")

    # ── published/ 아카이브 ────────────────────────────────────────
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    archive_path = os.path.join(PUBLISHED_DIR, post_filename)
    Path(archive_path).write_text(final_content, encoding="utf-8")

    # ── final/ 삭제 (중복 발행 방지) ──────────────────────────────
    target.unlink()
    review = target.parent / f"review_report_{target.stem}.txt"
    if review.exists():
        review.unlink()
    print(f"  🗑️  final/ 삭제: {target.name}")

    # ── 발행 URL 추정 ──────────────────────────────────────────────
    pub_url = f"https://frontbuffer.net/{cat}/{target_slug}-{target_ct.lower()}/"

    # ── cluster_name 역추적 ────────────────────────────────────────
    cluster_name = None
    for week_sels in pipeline.get("weekly_selections", {}).values():
        for sel in week_sels:
            if (slugify(sel.get("cluster_name", "")) == target_slug
                    and sel.get("content_type", "").upper() == target_ct):
                cluster_name = sel.get("cluster_name")
                break
        if cluster_name:
            break

    # ── write.py done 호출 ─────────────────────────────────────────
    if cluster_name:
        result = subprocess.run(
            ["python", "write.py", "done", cluster_name,
             "--type", target_ct, "--title", title, "--url", pub_url],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"  ⚠️ done 실패 (발행은 계속): {result.stderr[:200]}")
    else:
        print(f"  ⚠️ cluster_name 역추적 실패 — done 스킵")

    # ── GitHub Actions 환경변수 출력 ───────────────────────────────
    github_env = os.environ.get("GITHUB_ENV", "")
    if github_env:
        with open(github_env, "a") as env:
            env.write(f"POST_FILENAME={post_filename}\n")
            env.write(f"POST_TITLE={title}\n")
            env.write(f"POST_URL={pub_url}\n")

    print(f"\n✅ 발행 완료: {title}")
    print(f"   파일: {post_filename}")
    print(f"   URL:  {pub_url}")


if __name__ == "__main__":
    main()
