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
#      - 문제가 있는 파일(중복 의심, Gemini 메모 잔존 등)은 건너뛰고 다음 파일로 진행
#   2. 플레이스홀더 제거 ([INTERNAL LINK: ...] 등) — 매칭 실패 시 그 문장만 삭제
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
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

FINAL_DIR     = "research_data/write/final"
PUBLISHED_DIR = "research_data/write/published"
POSTS_DIR     = "_posts"
PIPELINE_FILE = "content_pipeline.json"
POSTS_FILE    = "posts.json"




# ── Gemini 간단 호출 (SEO 디스크립션 생성용) ──────────────────────
def call_gemini_simple(prompt_text, max_tokens=200):
    """단순 텍스트 생성용 Gemini 호출"""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model}:generateContent?key={api_key}")
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": max_tokens}
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            parts = (data.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}]))
            return "".join(p.get("text", "") for p in parts).strip()
    except Exception as e:
        print(f"  ⚠️ Gemini 호출 실패: {e}")
        return None
# ────────────────────────────────────────────────────────────────


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60].rstrip("-")


# ── 발행 보류 예외 ───────────────────────────────────────────────
class BlockedPost(Exception):
    """이 파일은 발행하지 않고 건너뛴다 (다음 파일로 진행)."""


# 제거된 플레이스홀더 표시용 마커 (문장 단위 삭제에 사용)
MARK = "\ue000"

STOPWORDS = {
    "a", "an", "and", "or", "the", "to", "of", "for", "in", "on", "at", "by",
    "with", "vs", "how", "what", "is", "are", "your", "you", "it", "its",
    "into", "from", "as", "be", "do", "does", "can", "features", "feature",
    "platform", "guide", "tips", "best", "new",
}


def drop_marked_sentences(text):
    """MARK가 들어 있는 문장만 삭제. (플레이스홀더 제거 후 '...guide on .' 같은 잔재 방지)"""
    out = []
    for line in text.split("\n"):
        if MARK not in line:
            out.append(line)
            continue
        stripped = line.lstrip()
        # 표/제목/인용 줄은 마커만 제거
        if stripped.startswith(("|", "#", ">")):
            out.append(line.replace(MARK, ""))
            continue
        sentences = re.split(r"(?<=[.!?])\s+", line)
        kept = [s for s in sentences if MARK not in s]
        new_line = " ".join(kept).strip()
        if new_line:
            out.append(new_line)
        # 남는 문장이 없으면 줄 전체 삭제
    return "\n".join(out)


def clean_excerpt(text):
    """excerpt에 마크다운 기호가 남지 않게 정리."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*`#>]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def cut_at_word(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-—")


def fallback_excerpt(body_lines, limit=155):
    """Gemini 없이 만드는 excerpt: 문장 단위로 limit 이내까지."""
    text = clean_excerpt(" ".join(body_lines[:4]))
    out = ""
    for s in re.split(r"(?<=[.!?])\s+", text):
        cand = (out + " " + s).strip()
        if len(cand) <= limit:
            out = cand
        else:
            break
    if len(out) >= 50:
        return out
    return cut_at_word(text, limit - 1) + "…"


def make_tags(target_ct, target_slug, title):
    words = [w for w in re.split(r"[-\s]+", target_slug.lower())
             if w and not w.isdigit() and w not in STOPWORDS and len(w) > 1]
    if len(words) < 2:
        title_words = [w for w in re.findall(r"[a-z0-9]+", title.lower())
                       if w not in STOPWORDS and not w.isdigit() and len(w) > 2]
        words += [w for w in title_words if w not in words]
    tags = list(dict.fromkeys([target_ct.lower()] + words[:4]))[:5]
    return ", ".join(f'"{t}"' for t in tags)


def _sig_words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower())
            if w not in STOPWORDS and len(w) > 1}


def _front_matter_title(path):
    try:
        with open(path, encoding="utf-8") as fh:
            for _ in range(15):
                line = fh.readline()
                if not line:
                    break
                m = re.match(r"^title:\s*(.+?)\s*$", line)
                if m:
                    t = m.group(1)
                    if len(t) >= 2 and t[0] == t[-1] and t[0] in "'\"":
                        t = t[1:-1].replace("''", "'")
                    return t
    except Exception:
        pass
    return ""


def find_duplicate(title, title_slug):
    """이미 발행된 글과 같은 슬러그이거나 제목이 거의 같으면 사유 문자열을 반환."""
    # 1) 같은 슬러그의 파일이 _posts/에 있는가
    pattern = re.compile(rf"^\d{{4}}-\d{{2}}-\d{{2}}-{re.escape(title_slug)}\.md$")
    for p in Path(POSTS_DIR).glob("*.md"):
        if pattern.match(p.name):
            return f"같은 슬러그 글이 이미 발행됨: {p.name}"

    # 2) 제목 유사도 (posts.json + _posts/ front matter 제목)
    words = _sig_words(title)
    if len(words) < 3:
        return None
    known = []
    try:
        if os.path.exists(POSTS_FILE):
            data = json.loads(open(POSTS_FILE, encoding="utf-8").read())
            known += [(p.get("title", ""), p.get("slug", "posts.json"))
                      for p in data.get("posts", [])]
    except Exception:
        pass
    for p in Path(POSTS_DIR).glob("*.md"):
        known.append((_front_matter_title(p), p.name))
    for t, where in known:
        w2 = _sig_words(t or "")
        if not w2:
            continue
        j = len(words & w2) / len(words | w2)
        if j >= 0.75:
            return f"제목이 거의 같은 글이 이미 있음({j:.0%}): {t} [{where}]"
    return None


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
            return MARK

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

        # ── 매칭 실패 또는 PENDING → 제거 (그 문장 전체 삭제) ─────
        removed += 1
        return MARK

    result = re.sub(r'\[INTERNAL LINK:([^\]]*)\](?!\()', replace_link, content)
    result = drop_marked_sentences(result)

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
    """HUB 글은 해당 클러스터의 모든 스포크 발행 완료 후에만 발행.
    hub_clusters[].spoke_urls 기준으로 PENDING이 없어야 함."""
    hub_clusters = pipeline.get("hub_clusters", {})

    # hub_clusters에서 해당 cluster_name의 허브 찾기
    for hub_key, hub_info in hub_clusters.items():
        spoke_urls = hub_info.get("spoke_urls", {})
        # cluster_name이 spoke_urls 키에 포함돼 있는지 확인
        matched = any(
            cluster_name.lower() in k.lower()
            for k in spoke_urls.keys()
            if "(HUB)" not in k
        )
        if not matched:
            continue
        # 스포크 URL 중 PENDING이나 빈 값이 있으면 아직 미완성
        spoke_only = {k: v for k, v in spoke_urls.items() if "(HUB)" not in k}
        if not spoke_only:
            return False
        all_published = all(
            v and v != "PENDING" and v.startswith("http")
            for v in spoke_only.values()
        )
        pending_count = sum(1 for v in spoke_only.values() if not v or v == "PENDING")
        print(f"  🔍 HUB 조건 체크: {hub_key} — 스포크 {len(spoke_only)}개 중 PENDING {pending_count}개")
        return all_published

    # hub_clusters에 없으면 기존 방식 fallback (발행된 스포크 2개 이상)
    published = pipeline.get("published", [])
    spokes = [p for p in published
              if p.get("cluster_name") == cluster_name
              and p.get("content_type", "").upper() != "HUB"]
    return len(spokes) >= 2


def prepare_post(target, target_slug, target_ct, pipeline, force=False):
    """파일 1개를 발행 가능한 형태로 가공. 문제가 있으면 BlockedPost를 발생시킨다."""
    content = target.read_text(encoding="utf-8")

    # ── 발행 불가 패턴 사전 차단 (원본 기준) ───────────────────────
    # [INTERNAL LINK: ...]는 아래에서 링크로 바꾸거나 문장째 삭제하므로
    # 여기서 막지 않고, 처리 후에도 남아 있을 때만 막는다.
    RAW_BLOCK_PATTERNS = [
        (r"\[cite:\s*\d+",           "Gemini cite 번호 잔존"),
        (r"cite:\s*\d+,\s*\d+",     "Gemini cite 연속 번호 잔존"),
        (r"판정 요약",                   "한국어 판정 메모 잔존"),
        (r"수정 내용 \+ 근거 URL",       "Gemini 검토 메모 잔존"),
    ]
    for bp, bp_desc in RAW_BLOCK_PATTERNS:
        if re.search(bp, content):
            raise BlockedPost(f"발행 불가 패턴 감지 — {bp_desc} ({target.name})")

    # ── H1에서 제목 추출 ───────────────────────────────────────────
    title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    title = (title_match.group(1).strip()
             if title_match else target_slug.replace("-", " ").title())

    # ── cluster_name 역추적 ───────────────────────────────────────
    cluster_name = None
    for week_sels in pipeline.get("weekly_selections", {}).values():
        for sel in week_sels:
            if (slugify(sel.get("cluster_name", "")) == target_slug
                    and sel.get("content_type", "").upper() == target_ct):
                cluster_name = sel.get("cluster_name")
                break
        if cluster_name:
            break

    # ── 날짜 / 카테고리 / URL ─────────────────────────────────────
    now      = datetime.now(timezone.utc)
    minute   = random.randint(0, 59)
    date_str = now.strftime("%Y-%m-%d")
    dt_str   = f"{date_str} 14:{minute:02d}:00 +0000"

    gaming_keys = ["steam", "game", "gaming", "xbox", "playstation",
                   "nintendo", "fallout", "portable", "handheld", "deck"]
    cat_check = (target_slug + " " + title.lower())
    cat = "gaming" if any(k in cat_check for k in gaming_keys) else "tech"

    title_slug    = slugify(title)
    post_filename = f"{date_str}-{title_slug}.md"
    pub_url       = f"https://frontbuffer.net/{cat}/{title_slug}/"

    hub_permalink = None
    if target_ct.upper() == "HUB":
        hub_permalink = f"/{cat}/{title_slug}/"
        pub_url = f"https://frontbuffer.net{hub_permalink}"

    # ── 중복 검사 (같은 슬러그 / 제목 유사) ────────────────────────
    if not force:
        dup = find_duplicate(title, title_slug)
        if dup:
            raise BlockedPost(f"중복 의심 — {dup} ({target.name})")

    # ── [INTERNAL LINK: xxx] → 실제 URL (미매칭이면 해당 문장 삭제) ─
    content = inject_internal_links(
        content, cluster_name or "", target_ct, pipeline, pub_url
    )

    # ── 나머지 플레이스홀더 제거 ───────────────────────────────────
    content = re.sub(r'\[AFFILIATE LINK:[^\]]*\](?!\()', '', content)
    content = re.sub(r'\[NEEDS VERIFICATION\]', '', content)
    content = re.sub(r'\[Source:[^\]]*\](?!\()', '', content)
    content = re.sub(r'[ \t]{2,}', ' ', content)
    content = re.sub(r'\n{3,}', '\n\n', content)

    # ── 처리 후에도 남은 내부링크는 최종 차단 ─────────────────────
    if re.search(r"\[INTERNAL LINK:", content):
        raise BlockedPost(f"발행 불가 패턴 감지 — 미처리 내부링크 잔존 ({target.name})")

    # ── 태그 ───────────────────────────────────────────────────────
    tags_str = make_tags(target_ct, target_slug, title)

    # ── excerpt (Gemini → 실패 시 문장 단위 폴백) ──────────────────
    body_lines = [l for l in content.splitlines()
                  if l.strip()
                  and not l.startswith("#")
                  and not l.startswith("---")
                  and not l.startswith("[SOURCES")]
    excerpt = ""
    try:
        body_preview = " ".join(body_lines)[:1500]
        seo_prompt = f"""Write a meta description for this article.

Title: {title}
Content preview: {body_preview}

Rules:
- 140-155 characters exactly
- Start with the most compelling fact or hook
- Do NOT start with "This article", "In this", "Learn", "Discover"
- No AI-sounding phrases
- Focus on what the reader will find out
- Must be unique and specific to this article

Return ONLY the meta description text. No quotes. No explanation."""
        seo_resp = call_gemini_simple(seo_prompt)
        if seo_resp:
            seo_resp = clean_excerpt(seo_resp).strip("\"' ")
        if seo_resp and 50 < len(seo_resp) < 200:
            excerpt = cut_at_word(seo_resp, 155)
    except Exception as e:
        print(f"  ⚠️ SEO excerpt 생성 실패 (폴백 사용): {e}")
    if not excerpt:
        excerpt = fallback_excerpt(body_lines)

    yaml_title   = title.replace("'", "''")
    yaml_excerpt = excerpt.replace("'", "''")

    # ── front matter ───────────────────────────────────────────────
    permalink_line = f"permalink: '{hub_permalink}'\n" if hub_permalink else ""
    front_matter = (
        f"---\n"
        f"layout: single\n"
        f"title: '{yaml_title}'\n"
        f"date: {dt_str}\n"
        f"categories: [{cat}]\n"
        f"tags: [{tags_str}]\n"
        f"excerpt: '{yaml_excerpt}'\n"
        f"{permalink_line}"
        f"author_profile: false\n"
        f"read_time: true\n"
        f"share: true\n"
        f"---\n\n"
    )

    # ── 기존 front matter 제거 ────────────────────────────────────
    if content.lstrip().startswith('---'):
        fm_end = content.find('---', content.find('---') + 3)
        if fm_end != -1:
            content = content[fm_end + 3:].lstrip()

    # ── H1 + 소스 헤더 제거 ────────────────────────────────────────
    body = re.sub(r'^# .+\n', '', content, count=1, flags=re.MULTILINE)
    body = re.sub(r'^\[SOURCES USED:.*\]\n?', '', body, flags=re.MULTILINE)
    body = re.sub(r'^\[DISCARDED:.*\]\n?', '', body, flags=re.MULTILINE)

    return {
        "title":         title,
        "cat":           cat,
        "cluster_name":  cluster_name,
        "pub_url":       pub_url,
        "post_filename": post_filename,
        "final_content": front_matter + body.lstrip(),
        "date_str":      date_str,
    }


def main():
    pipeline = load_pipeline()
    force = os.environ.get("FORCE_PUBLISH", "").strip().lower() == "true"

    # ── final/ 파일 목록 (publish_order 기반 FIFO) ──────────────────
    # 파일명 형식: {order:03d}_{week_tag}_{folder_id}_{CT}.md
    # 앞 3자리 숫자가 Step 2에서 정한 발행 순서.
    # 숫자 없는 구버전 파일은 맨 뒤로 (88999 처리).
    def _sort_key(f, hub_ready_names=None):
        name   = f.name
        prefix = name.split("_")[0]
        if prefix.upper().startswith("H"):
            try:
                hub_num = int(prefix[1:])
            except ValueError:
                hub_num = 999
            stem  = f.stem
            h_fmt = re.match(r'^H\d+_\d{4}-W\d+_(.+)_HUB$', stem)
            slug  = h_fmt.group(1) if h_fmt else stem
            ready = hub_ready_names and slug in hub_ready_names
            order = hub_num - 10000 if ready else 99000 + hub_num
        else:
            try:
                order = int(prefix)
            except (ValueError, IndexError):
                order = 88999
        return (order, name)

    # hub_ready 조건 충족된 HUB slug 목록 미리 계산
    _hub_ready_slugs = set()
    for _f in Path(FINAL_DIR).glob("H*.md"):
        _stem  = _f.stem
        _h_fmt = re.match(r'^H\d+_\d{4}-W\d+_(.+)_HUB$', _stem)
        if not _h_fmt:
            continue
        _slug = _h_fmt.group(1)
        _cn   = None
        for _ws in pipeline.get("weekly_selections", {}).values():
            for _s in _ws:
                if slugify(_s.get("cluster_name","")) == _slug and _s.get("content_type","").upper() == "HUB":
                    _cn = _s.get("cluster_name")
                    break
            if _cn:
                break
        if _cn and hub_ready(pipeline, _cn):
            _hub_ready_slugs.add(_slug)

    final_files = sorted(
        [f for f in Path(FINAL_DIR).glob("*.md")
         if not f.name.startswith("review_report_")],
        key=lambda f: _sort_key(f, _hub_ready_slugs)
    )

    if not final_files:
        print("ℹ️  발행할 파일 없음 — 종료")
        sys.exit(0)

    # ── 발행 대상 선택 (문제 파일은 건너뛰고 다음 파일로) ──────────
    target = None
    target_slug = None
    target_ct   = None
    prep = None
    skipped_hubs = []
    blocked = []

    for f in final_files:
        stem  = f.stem
        new_fmt = re.match(r'^(?:H)?\d+_\d{4}-W\d+_(.+)_([A-Z]+)$', stem)
        if new_fmt:
            slug, ct = new_fmt.group(1), new_fmt.group(2).upper()
        else:
            parts = stem.rsplit("_", 1)
            if len(parts) != 2:
                continue
            slug, ct = parts[0], parts[1].upper()

        # 이미 발행된 파일 스킵 (posts.json 1차, pipeline published 2차)
        already = False
        try:
            if os.path.exists(POSTS_FILE):
                posts_data = json.loads(open(POSTS_FILE, encoding="utf-8").read())
                for post in posts_data.get("posts", []):
                    live_url = post.get("live_url", "")
                    if slug.replace("-", "") in live_url.replace("-", ""):
                        post_ct = post.get("content_type", "").upper()
                        if post_ct == ct:
                            already = True
                            break
        except Exception:
            pass

        if not already:
            already = any(
                slugify(p.get("cluster_name", "")) == slug
                and p.get("content_type", "").upper() == ct
                and p.get("url", "pending").lower() not in ("pending", "", None)
                for p in pipeline.get("published", [])
            )

        if already:
            print(f"  ⏭️  이미 발행됨 — 스킵: {f.name}")
            continue

        # HUB 조건 체크
        if ct == "HUB":
            hub_cn = None
            for week_sels in pipeline.get("weekly_selections", {}).values():
                for sel in week_sels:
                    if (slugify(sel.get("cluster_name", "")) == slug
                            and sel.get("content_type", "").upper() == "HUB"):
                        hub_cn = sel.get("cluster_name")
                        break
                if hub_cn:
                    break

            if hub_cn and not hub_ready(pipeline, hub_cn):
                skipped_hubs.append(f.name)
                print(f"  ⏳ HUB 보류 (스포크 2개 미만): {f.name}")
                continue

        # 발행 가능 여부 점검 (문제 있으면 건너뛰고 알림)
        try:
            prep = prepare_post(f, slug, ct, pipeline, force=force)
        except BlockedPost as e:
            reason = str(e)
            blocked.append(reason)
            print(f"🚨 발행 보류 — {reason}")
            print(f"::warning title=발행 보류::{reason}")
            subprocess.run(
                ["python", "notify.py", "step4_fail", "--reason", reason],
                check=False
            )
            prep = None
            continue

        target      = f
        target_slug = slug
        target_ct   = ct
        break

    if not target:
        if blocked:
            print(f"❌ 발행 가능한 파일이 없음 — 보류 {len(blocked)}개 (위 사유 확인)")
            sys.exit(1)
        if skipped_hubs:
            print(f"ℹ️  발행 가능한 파일 없음 (HUB 보류: {len(skipped_hubs)}개)")
        else:
            print("ℹ️  발행할 파일 없음 — 종료")
        sys.exit(0)

    print(f"\n📤 발행 대상: {target.name}")
    if blocked:
        print(f"⚠️  이번에 건너뛴 파일 {len(blocked)}개 — final/ 에 그대로 남아 있음")

    title         = prep["title"]
    cat           = prep["cat"]
    cluster_name  = prep["cluster_name"]
    pub_url       = prep["pub_url"]
    post_filename = prep["post_filename"]
    final_content = prep["final_content"]
    date_str      = prep["date_str"]

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
    if cluster_name:
        pipeline = update_pipeline_urls(pipeline, cluster_name, target_ct, pub_url)

    # ── write.py done 호출 ─────────────────────────────────────────
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

    # ── posts.json 업데이트 ───────────────────────────────────────
    try:
        posts_data = {"posts": []}
        if os.path.exists(POSTS_FILE):
            posts_data = json.loads(open(POSTS_FILE, encoding="utf-8").read())

        existing_urls = {p.get("live_url", "") for p in posts_data.get("posts", [])}

        if pub_url not in existing_urls:
            hub_cluster = ""
            kws = []
            if cluster_name:
                pipeline_reload = load_pipeline()
                for week_sels in pipeline_reload.get("weekly_selections", {}).values():
                    for sel in week_sels:
                        if sel.get("cluster_name", "").lower() == cluster_name.lower():
                            hub_cluster = sel.get("cluster_name", "")
                            hw = sel.get("hub_keyword", "")
                            sw = sel.get("spoke_keywords", [])[:2]
                            kws = ([hw] + sw) if hw else sw
                            break
                    if hub_cluster:
                        break

            post_entry = {
                "status":            "live",
                "date":              date_str,
                "title":             title,
                "live_url":          pub_url,
                "categories":        [cat],
                "content_type":      target_ct,
                "hub_cluster":       hub_cluster or cluster_name or "",
                "verified_keywords": kws,
                "slug":              post_filename[:-3],
            }
            posts_data["posts"].append(post_entry)
            posts_data["posts"].sort(key=lambda x: x.get("date", ""))
            open(POSTS_FILE, "w", encoding="utf-8").write(
                json.dumps(posts_data, ensure_ascii=False, indent=2)
            )
            print(f"  📋 posts.json 업데이트: {pub_url}")
        else:
            print(f"  ℹ️  posts.json 이미 존재: {pub_url}")
    except Exception as e:
        print(f"  ⚠️ posts.json 업데이트 실패 (발행은 완료): {e}")

    print(f"\n✅ 발행 완료: {title}")
    print(f"   파일: {post_filename}")
    print(f"   URL:  {pub_url}")


if __name__ == "__main__":
    main()
