# =====================================================================
# 📚 글 목록 관리 (posts_manager.py)
# =====================================================================
# 역할: 발행된 글 전체 목록을 posts.json에 독립 관리
#       - 허브+스포크 연결 추적
#       - [INTERNAL LINK] 플레이스홀더 → 실제 URL 교체
#       - Jekyll 세팅 후 _data/posts.json으로 그대로 복사 가능
#
# posts.json 스키마:
#   id:                     slug (고유 식별자)
#   title:                  발행 제목
#   slug:                   URL slug
#   url:                    현재 URL (draft_url or 실제 URL)
#   live_url:               실제 블로그 URL (Jekyll 발행 후)
#   published_date:         발행일 (YYYY-MM-DD)
#   content_type:           GUIDE/COMPARISON/EXPLAINER/LISTICLE
#   hub_cluster:            parent_hub (허브 클러스터명)
#   hub_keyword:            Trends/KP 검색 키워드
#   verified_keywords:      KP 발굴 롱테일 키워드
#   data_grade:             A/B/C
#   internal_links_needed:  ["[INTERNAL LINK: ...]"] 플레이스홀더 목록
#   internal_links_resolved:{플레이스홀더: 실제 URL} 교체 완료 목록
#   status:                 draft_url / live / internal_linked
# =====================================================================

import os
import re
import json
import shutil
from datetime import datetime, timezone

POSTS_FILE    = "posts.json"
PUBLISHED_DIR = os.path.join("research_data", "write", "published")


def load_posts():
    try:
        with open(POSTS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "_version":     "1.0",
            "_description": "발행된 글 전체 목록 — 허브+스포크 연결 관리",
            "posts":        [],
        }


def save_posts(data):
    data["_last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _slugify(text):
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def _extract_internal_links(md_text):
    """MD 파일에서 [INTERNAL LINK: ...] 플레이스홀더 추출."""
    return re.findall(r"\[INTERNAL LINK: ([^\]]+)\]", md_text)


# =====================================================================
# 글 등록 (발행 기록 시 자동 호출)
# =====================================================================

def register_post(cluster_info, title, url, published_date=None):
    """
    발행 기록 시 posts.json에 자동 등록.
    write.py의 record_publish()가 호출.
    """
    data  = load_posts()
    slug  = _slugify(title)
    today = published_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 이미 등록된 경우 URL만 업데이트
    for post in data["posts"]:
        if post["id"] == slug:
            post["url"] = url
            if url and not url.startswith("/drafts"):
                post["live_url"] = url
                post["status"]   = "live"
            save_posts(data)
            return post

    # final MD에서 INTERNAL LINK 플레이스홀더 추출
    _slug = _slugify(cluster_info.get("cluster_name", title))
    _ct   = (cluster_info.get("content_type", "") or "").upper().strip()
    _fn   = f"{_slug}_{_ct}.md" if _ct else f"{_slug}.md"
    final_path = os.path.join("research_data", "write", "final", _fn)
    # 구버전 fallback (읽기 전용이므로 안전)
    if not os.path.exists(final_path):
        _legacy = os.path.join("research_data", "write", "final", f"{_slug}.md")
        if os.path.exists(_legacy):
            final_path = _legacy
    internal_links_needed = []
    if os.path.exists(final_path):
        md_text = open(final_path, encoding="utf-8").read()
        internal_links_needed = [
            f"[INTERNAL LINK: {m}]"
            for m in _extract_internal_links(md_text)
        ]

    cluster_slug = _slugify(cluster_info.get("cluster_name", title))
    post = {
        "id":                      slug,
        "title":                   title,
        "slug":                    slug,
        "cluster_slug":            cluster_slug,  # published/ 파일명 매칭용
        "url":                     url,
        "live_url":                "" if url.startswith("/drafts") else url,
        "published_date":          today,
        "content_type":            cluster_info.get("content_type", ""),
        "hub_cluster":             cluster_info.get("parent_hub", ""),
        "hub_keyword":             cluster_info.get("hub_keyword", ""),
        "verified_keywords":       [
            v["keyword"] for v in cluster_info.get("verified_keywords", [])[:5]
        ],
        "data_grade":              cluster_info.get("data_grade", ""),
        "internal_links_needed":   internal_links_needed,
        "internal_links_resolved": {},
        "status":                  "draft_url" if url.startswith("/drafts") else "live",
    }
    data["posts"].append(post)
    save_posts(data)
    return post


# =====================================================================
# URL 업데이트 (Jekyll 발행 후 실제 URL 등록)
# =====================================================================

def update_live_url(slug_or_title, live_url):
    """
    Jekyll 발행 후 실제 URL 등록.
    자동으로 published/ MD 파일의 front matter도 업데이트.
    """
    data = load_posts()
    slug = _slugify(slug_or_title)
    updated = False

    for post in data["posts"]:
        if post["id"] == slug or _slugify(post["title"]) == slug:
            post["live_url"] = live_url
            post["url"]      = live_url
            post["status"]   = "live"
            updated = True
            break

    if updated:
        save_posts(data)
    return updated


# =====================================================================
# INTERNAL LINK 교체
# =====================================================================

def resolve_internal_links(hub_name, hub_url):
    """
    허브 URL이 확정되면 모든 스포크 MD 파일의
    [INTERNAL LINK: ...] 플레이스홀더를 실제 링크로 교체.
    반환: 교체된 파일 목록
    """
    data    = load_posts()
    changed = []

    for post in data["posts"]:
        needed = post.get("internal_links_needed", [])
        if not needed:
            continue

        # 이 포스트에 hub_name 관련 플레이스홀더가 있는지 확인
        matching = [
            link for link in needed
            if hub_name.lower() in link.lower()
            and link not in post.get("internal_links_resolved", {})
        ]
        if not matching:
            continue

        # published/ MD 파일 찾기
        pub_path = _find_published_file(post["slug"], post.get("cluster_slug"))
        if not pub_path:
            continue

        md_text = open(pub_path, encoding="utf-8").read()
        modified = md_text

        for placeholder in matching:
            # [INTERNAL LINK: Hub Topic] → [Hub Topic](hub_url)
            inner = re.search(r"\[INTERNAL LINK: ([^\]]+)\]", placeholder)
            if inner:
                anchor_text = inner.group(1)
                replacement = f"[{anchor_text}]({hub_url})"
                modified    = modified.replace(placeholder, replacement)
            post.setdefault("internal_links_resolved", {})[placeholder] = hub_url

        if modified != md_text:
            open(pub_path, "w", encoding="utf-8").write(modified)
            changed.append(pub_path)

            # 모든 플레이스홀더가 교체됐으면 status 업데이트
            resolved = set(post.get("internal_links_resolved", {}).keys())
            needed_set = set(needed)
            if needed_set.issubset(resolved):
                post["status"] = "internal_linked"

    if changed:
        save_posts(data)
    return changed


def _find_published_file(slug, cluster_slug=None):
    """published/ 폴더에서 slug에 해당하는 MD 파일 찾기.
    파일명: YYYY-MM-DD-{cluster_slug}.md
    cluster_slug가 있으면 정확 매칭, 없으면 유사도 매칭.
    """
    if not os.path.exists(PUBLISHED_DIR):
        return None
    # cluster_slug 정확 매칭 (우선)
    if cluster_slug:
        for fname in os.listdir(PUBLISHED_DIR):
            if cluster_slug in fname and fname.endswith(".md"):
                return os.path.join(PUBLISHED_DIR, fname)
    slug_words = set(slug.split("-")) - {"how", "to", "a", "an", "the", "and", "or"}
    best_match = None
    best_score = 0
    for fname in os.listdir(PUBLISHED_DIR):
        if not fname.endswith(".md"):
            continue
        # 날짜 접두어 제거 후 비교
        name_part = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", fname[:-3])
        name_words = set(name_part.split("-")) - {"how", "to", "a", "an", "the"}
        score = len(slug_words & name_words)
        if score > best_score:
            best_score = score
            best_match = os.path.join(PUBLISHED_DIR, fname)
    return best_match if best_score >= 2 else None


# =====================================================================
# 조회 유틸
# =====================================================================

def get_posts_by_hub(hub_name):
    """특정 허브 클러스터의 스포크 글 목록."""
    data = load_posts()
    return [p for p in data["posts"]
            if p.get("hub_cluster", "").lower() == hub_name.lower()]


def get_unresolved_links():
    """INTERNAL LINK 플레이스홀더가 남아있는 글 목록."""
    data = load_posts()
    result = []
    for post in data["posts"]:
        needed   = set(post.get("internal_links_needed", []))
        resolved = set(post.get("internal_links_resolved", {}).keys())
        pending  = needed - resolved
        if pending:
            result.append({"post": post, "pending": list(pending)})
    return result


def get_hub_summary():
    """허브별 스포크 발행 현황 요약."""
    data = load_posts()
    hubs = {}
    for post in data["posts"]:
        hub = post.get("hub_cluster", "미분류")
        if hub not in hubs:
            hubs[hub] = {"spokes": [], "live": 0, "linked": 0}
        hubs[hub]["spokes"].append(post)
        if post["status"] in ("live", "internal_linked"):
            hubs[hub]["live"] += 1
        if post["status"] == "internal_linked":
            hubs[hub]["linked"] += 1
    return hubs


# =====================================================================
# CLI
# =====================================================================

if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "status":
        data  = load_posts()
        posts = data.get("posts", [])
        print(f"\n📚 전체 글 목록 ({len(posts)}편)")
        print("=" * 60)

        hubs = get_hub_summary()
        for hub, info in hubs.items():
            print(f"\n🔷 {hub} ({info['live']}/{len(info['spokes'])}편 라이브)")
            for p in info["spokes"]:
                icon = {"draft_url": "⬜", "live": "✅",
                        "internal_linked": "🔗"}.get(p["status"], "❓")
                pending = len(p.get("internal_links_needed", [])) - \
                          len(p.get("internal_links_resolved", {}))
                link_txt = f" [{pending}개 링크 미교체]" if pending > 0 else ""
                print(f"  {icon} {p['title']}{link_txt}")
                if p.get("live_url"):
                    print(f"     → {p['live_url']}")

        unresolved = get_unresolved_links()
        if unresolved:
            print(f"\n⚠️  INTERNAL LINK 미교체: {len(unresolved)}건")
            for item in unresolved:
                print(f"  {item['post']['title']}: {item['pending']}")

    elif cmd == "resolve":
        if len(sys.argv) < 4:
            print("사용법: python posts_manager.py resolve <hub_name> <hub_url>")
            sys.exit(1)
        hub_name, hub_url = sys.argv[2], sys.argv[3]
        changed = resolve_internal_links(hub_name, hub_url)
        print(f"✅ {len(changed)}개 파일 링크 교체 완료: {changed}")

    elif cmd == "update-url":
        if len(sys.argv) < 4:
            print("사용법: python posts_manager.py update-url <slug> <live_url>")
            sys.exit(1)
        slug, url = sys.argv[2], sys.argv[3]
        ok = update_live_url(slug, url)
        print(f"{'✅' if ok else '❌'} URL 업데이트: {slug} → {url}")
