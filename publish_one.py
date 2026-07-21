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


def inject_internal_links(content, cluster_name, content_type, pipeline, pub_url):
    """[INTERNAL LINK: xxx] 플레이스홀더를 실제 URL로 교체.

    교체 우선순위:
      1. [INTERNAL LINK: HUB]      → 이 글의 parent HUB URL
      2. [INTERNAL LINK: 스포크명]  → spoke_urls에서 키 부분 매칭
      3. URL이 PENDING이거나 매칭 실패 → 제거 (기존 동작 유지)

    content_pipeline.json 구조:
      hub_clusters[hub_keyword] = {
        "spoke_urls": { "클러스터명 (TYPE)": "https://..." },
        "hub_url": "https://..."   ← HUB 발행 후 채워짐 (현재 비어있을 수 있음)
      }
    """
    hub_clusters = pipeline.get("hub_clusters", {})

    # ── 이 글의 parent_hub 찾기 ──────────────────────────────────
    parent_hub = None
    for week_sels in pipeline.get("weekly_selections", {}).values():
        for sel in week_sels:
            if (sel.get("cluster_name") == cluster_name
                    and sel.get("content_type", "").upper() == content_type):
                parent_hub = sel.get("parent_hub") or sel.get("hub_keyword")
                break
        if parent_hub:
            break

    # published 목록에서도 탐색 (fallback)
    if not parent_hub:
        for p in pipeline.get("published", []):
            if (p.get("cluster_name") == cluster_name
                    and p.get("content_type", "").upper() == content_type):
                parent_hub = p.get("hub_cluster")
                break

    hub_info   = hub_clusters.get(parent_hub, {}) if parent_hub else {}
    spoke_urls = hub_info.get("spoke_urls", {})
    hub_url    = hub_info.get("hub_url", "")

    injected = 0
    removed  = 0

    def replace_link(m):
        nonlocal injected, removed
        label = m.group(1).strip()   # [INTERNAL LINK: label] 의 label 부분

        # ── HUB 링크 ─────────────────────────────────────────────
        if label.upper() == "HUB":
            # HUB 글 자신이 발행될 때 pub_url이 곧 HUB URL
            url = pub_url if content_type == "HUB" else hub_url
            if url and url != "PENDING" and url.startswith("http"):
                injected += 1
                return f"[{hub_info.get('hub_keyword', label)}]({url})"
            removed += 1
            return ""

        # ── 스포크 링크 — spoke_urls 키에서 label 포함 여부로 매칭 ─
        matched_url = None
        label_lower = label.lower()
        for key, url in spoke_urls.items():
            # key 형식: "클러스터명 (TYPE)" — 클러스터명 부분만 비교
            key_name = re.sub(r'\s*\([^)]+\)\s*$', '', key).strip().lower()
            if label_lower in key_name or key_name in label_lower:
                if url and url != "PENDING" and url.startswith("http"):
                    matched_url = url
                    break   # 첫 번째 매칭 URL 사용

        if matched_url:
            injected += 1
            return f"[{label}]({matched_url})"

        # ── 매칭 실패 또는 PENDING → 제거 ────────────────────────
        removed += 1
        return ""

    result = re.sub(r'\[INTERNAL LINK:([^\]]*)\](?!\()', replace_link, content)

    if injected or removed:
        print(f"  🔗 내부 링크: {injected}개 주입 / {removed}개 제거 (PENDING 또는 미매칭)")

    return result


def update_pipeline_urls(pipeline, cluster_name, content_type, pub_url):
    """발행 완료 시 content_pipeline.json의 hub_clusters URL 업데이트.

    - 스포크 발행: spoke_urls["클러스터명 (TYPE)"] PENDING → 실제 URL
    - HUB 발행:   hub_clusters[parent_hub]["hub_url"] → 실제 URL
                  hub_status → "PUBLISHED"
    """
    hub_clusters = pipeline.get("hub_clusters", {})
    ct = content_type.upper()
    updated = False

    for hub_key, hub_info in hub_clusters.items():
        spoke_urls = hub_info.get("spoke_urls", {})

        if ct == "HUB":
            # HUB 글 자신: hub_url + hub_status 업데이트
            # spoke_urls 키에서 cluster_name + HUB 타입 매칭
            for key in list(spoke_urls.keys()):
                key_name = re.sub(r'\s*\([^)]+\)\s*$', '', key).strip().lower()
                if cluster_name.lower() in key_name or key_name in cluster_name.lower():
                    if "(HUB)" in key or "(hub)" in key.lower():
                        spoke_urls[key] = pub_url
                        hub_info["hub_url"]    = pub_url
                        hub_info["hub_status"] = "PUBLISHED"
                        updated = True
                        print(f"  📌 hub_url 업데이트: {hub_key} → {pub_url}")
                        break
        else:
            # 스포크 글: spoke_urls에서 cluster_name + TYPE 매칭
            target_key = None
            for key in spoke_urls:
                key_name = re.sub(r'\s*\([^)]+\)\s*$', '', key).strip().lower()
                key_type = re.search(r'\(([^)]+)\)', key)
                key_type = key_type.group(1).upper() if key_type else ""
                if (cluster_name.lower() in key_name or key_name in cluster_name.lower()) \
                        and key_type == ct:
                    target_key = key
                    break

            if target_key and spoke_urls.get(target_key) in ("PENDING", "", None):
                spoke_urls[target_key] = pub_url
                # internal_links 배열도 동기화
                links = hub_info.get("internal_links", [])
                try:
                    idx = links.index("PENDING")
                    links[idx] = pub_url
                except ValueError:
                    pass
                updated = True
                print(f"  📌 spoke_url 업데이트: {target_key} → {pub_url}")

    if updated:
        with open(PIPELINE_FILE, "w", encoding="utf-8") as f:
            json.dump(pipeline, f, ensure_ascii=False, indent=2)
        print(f"  💾 content_pipeline.json 저장 완료")
    else:
        print(f"  ℹ️  pipeline URL 업데이트 대상 없음 (이미 등록됐거나 키 미매칭)")

    return pipeline


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

    # ── cluster_name 역추적 (링크 주입에 필요하므로 앞으로 이동) ──
    cluster_name = None
    for week_sels in pipeline.get("weekly_selections", {}).values():
        for sel in week_sels:
            if (slugify(sel.get("cluster_name", "")) == target_slug
                    and sel.get("content_type", "").upper() == target_ct):
                cluster_name = sel.get("cluster_name")
                break
        if cluster_name:
            break

    # ── 발행 URL (링크 주입 시 HUB 자신의 URL로 사용) ─────────────
    # 이 시점엔 post_filename이 아직 없으므로 미리 계산
    now      = datetime.now(timezone.utc)
    minute   = random.randint(0, 59)
    date_str = now.strftime("%Y-%m-%d")
    dt_str   = f"{date_str} 14:{minute:02d}:00 +0000"

    gaming_keys = ["steam", "game", "gaming", "xbox", "playstation",
                   "nintendo", "fallout", "portable", "handheld", "deck"]
    cat = "gaming" if any(k in target_slug for k in gaming_keys) else "tech"

    post_filename = f"{date_str}-{target_slug}_{target_ct.lower()}.md"
    jekyll_slug   = post_filename[len(date_str) + 1:-3]
    pub_url       = f"https://frontbuffer.net/{cat}/{jekyll_slug}/"

    # ── [INTERNAL LINK: xxx] → 실제 URL 주입 (PENDING/미매칭은 제거) ─
    content = inject_internal_links(
        content, cluster_name or "", target_ct, pipeline, pub_url
    )

    # ── 나머지 플레이스홀더 제거 ───────────────────────────────────
    # 마크다운 링크 [text](url) 형태는 건드리지 않는다.
    # → [Source: X](url) 처럼 뒤에 (가 오면 앵커만 지워져 (url) 노출되므로
    #   뒤에 (가 없는 경우만 제거
    content = re.sub(r'\[AFFILIATE LINK:[^\]]*\](?!\()', '', content)
    content = re.sub(r'\[NEEDS VERIFICATION\]', '', content)
    content = re.sub(r'\[Source:[^\]]*\](?!\()', '', content)
    # 제거 후 남는 이중 공백/빈 줄 정리
    content = re.sub(r'[ \t]{2,}', ' ', content)
    content = re.sub(r'\n{3,}', '\n\n', content)

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
    post_path = os.path.join(POSTS_DIR, post_filename)
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

    # ── content_pipeline.json URL 업데이트 ────────────────────────
    # 스포크: spoke_urls PENDING → 실제 URL
    # HUB:   hub_url + hub_status 업데이트
    if cluster_name:
        pipeline = update_pipeline_urls(pipeline, cluster_name, target_ct, pub_url)

    # ── write.py done 호출 ─────────────────────────────────────────
    # --no-archive: 위에서 이미 published/ 아카이브를 만들었으므로
    #               record_publish의 중복 아카이브를 막는다.
    #               (안 막으면 final/ 파일이 이미 삭제된 상태라
    #                fallback 경로를 타 엉뚱한 파일을 아카이브함)
    if cluster_name:
        result = subprocess.run(
            ["python", "write.py", "done", cluster_name,
             "--type", target_ct, "--title", title, "--url", pub_url,
             "--no-archive"],
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
