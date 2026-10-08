# =====================================================================
# 🛡️ 주제 중복 방지 모듈 (topic_guard.py)
# =====================================================================
# 역할: 이미 발행된 글과 새 기획안/초안이 같은 주제인지 판단하고,
#       글쓰기 프롬프트에 넣을 "기존 글 목록 / 관련 글 링크"를 만들어 준다.
#
# 사용처:
#   research_gemini.py → Step 2: 기획안 프롬프트에 기존 글 목록 주입,
#                         기존 글과 겹치는 기획안 자동 제외
#   write.py           → Step 3: 글쓰기 프롬프트에 관련 글(실제 URL) 목록 주입
#
# 판단 기준 (config.json → topic_guard):
#   - 제목 단어 겹침(Jaccard)이 title_jaccard 이상이면 중복
#   - 기획안 제목 단어의 coverage 이상이 기존 글 제목에 들어 있고,
#     공유 단어가 min_shared_words 이상이면 중복
#   - HUB는 스포크를 묶는 글이라 검사에서 제외
# =====================================================================

import os
import re
import json
from pathlib import Path

POSTS_DIR   = "_posts"
POSTS_FILE  = "posts.json"
SITE_URL    = "https://frontbuffer.net"

DEFAULTS = {
    "enabled":              True,
    "title_jaccard":        0.60,
    "coverage":             0.80,
    "min_shared_words":     4,
    "max_titles_in_prompt": 120,
    "max_related_links":    5,
    "allow_duplicates":     [],      # 의도적으로 허용할 기획안 cluster_name 목록
    "block_speculative":    True,    # 출시 전 추측형 제목 제외
}

SPECULATIVE_MARKERS = (
    "anticipated", "anticipating", "rumored", "rumoured", "speculative",
    "envisioning", "what to expect", "expected to", "leaked",
)

STOPWORDS = {
    "a", "an", "and", "or", "the", "to", "of", "for", "in", "on", "at", "by",
    "with", "vs", "versus", "how", "what", "is", "are", "your", "you", "it",
    "its", "into", "from", "as", "be", "do", "does", "can", "which", "when",
    "why", "should", "will", "not", "this", "that", "new", "best", "guide",
    "tips", "complete", "explained", "compared", "comparison", "differences",
    "difference", "features", "feature", "2025", "2026", "2027",
}


def load_settings():
    cfg = dict(DEFAULTS)
    try:
        data = json.loads(open("config.json", encoding="utf-8").read())
        cfg.update(data.get("topic_guard", {}))
    except Exception:
        pass
    return cfg


def _norm_word(w):
    # 단순 복수형 정규화 (googlebooks → googlebook)
    if len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def title_words(text):
    words = set()
    for w in re.findall(r"[a-z0-9]+", (text or "").lower()):
        if w in STOPWORDS or len(w) < 2:
            continue
        words.add(_norm_word(w))
    return words


def _unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        v = v[1:-1]
        v = v.replace("''", "'")
    return v


def _front_matter(path):
    """_posts 파일의 front matter 일부(title, categories, permalink)만 읽는다."""
    out = {"title": "", "category": "tech", "permalink": ""}
    try:
        with open(path, encoding="utf-8") as fh:
            first = fh.readline()
            if not first.startswith("---"):
                return out
            for _ in range(40):
                line = fh.readline()
                if not line or line.startswith("---"):
                    break
                m = re.match(r"^title:\s*(.+?)\s*$", line)
                if m:
                    out["title"] = _unquote(m.group(1))
                m = re.match(r"^categories:\s*\[(.+?)\]", line)
                if m:
                    out["category"] = m.group(1).split(",")[0].strip().strip("'\"") or "tech"
                m = re.match(r"^permalink:\s*(.+?)\s*$", line)
                if m:
                    out["permalink"] = _unquote(m.group(1))
    except Exception:
        pass
    return out


def load_existing_posts():
    """발행된 글 목록: [{title, url, category, source}] — _posts 기준, posts.json은 보조."""
    items, seen = [], set()

    posts_dir = Path(POSTS_DIR)
    if posts_dir.is_dir():
        for p in sorted(posts_dir.glob("*.md")):
            m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$", p.name)
            if not m:
                continue
            fm = _front_matter(p)
            if not fm["title"]:
                continue
            slug = m.group(1).rstrip("-")          # Jekyll은 끝의 '-'를 제거함
            if fm["permalink"]:
                url = SITE_URL + fm["permalink"]
            else:
                url = f"{SITE_URL}/{fm['category']}/{slug}/"
            key = fm["title"].lower()
            if key in seen:
                continue
            seen.add(key)
            items.append({"title": fm["title"], "url": url,
                          "category": fm["category"], "source": p.name})

    # posts.json에만 있는 글(원래 제목)도 비교 대상에 포함 (수정 전 제목 대비)
    try:
        if os.path.exists(POSTS_FILE):
            data = json.loads(open(POSTS_FILE, encoding="utf-8").read())
            for post in data.get("posts", []):
                t = post.get("title", "")
                if t and t.lower() not in seen:
                    seen.add(t.lower())
                    cats = post.get("categories") or ["tech"]
                    items.append({"title": t, "url": post.get("live_url", ""),
                                  "category": cats[0], "source": "posts.json"})
    except Exception:
        pass
    return items


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def find_overlap(candidate_title, existing, settings=None):
    """candidate_title이 기존 글과 같은 주제면 (기존 제목, 근거 문자열)을 반환."""
    s = settings or load_settings()
    cw = title_words(candidate_title)
    if len(cw) < 3:
        return None
    for ex in existing:
        ew = title_words(ex["title"])
        if not ew:
            continue
        shared = cw & ew
        j = _jaccard(cw, ew)
        if j >= s["title_jaccard"]:
            return ex, f"제목 유사 {j:.0%}"
        cov = len(shared) / len(cw)
        if cov >= s["coverage"] and len(shared) >= s["min_shared_words"]:
            return ex, f"기존 제목에 {cov:.0%} 포함"
    return None


def selection_title(sel):
    """기획안 dict에서 비교용 제목을 뽑는다."""
    t = sel.get("suggested_title") or ""
    if t:
        return t
    parts = [sel.get("cluster_name", ""), sel.get("hub_keyword", "")]
    return " ".join(p for p in parts if p)


def filter_duplicate_selections(selections, existing=None, settings=None):
    """기획안 목록에서 (1) 기존 글과 겹치는 것 (2) 같은 배치 안에서 서로 겹치는 것을 제외.
    HUB와 allow_duplicates는 검사하지 않는다.
    반환: (남은 기획안, [(제외된 기획안, 사유)])"""
    s = settings or load_settings()
    if not s.get("enabled", True):
        return selections, []
    existing = existing if existing is not None else load_existing_posts()
    kept, dropped = [], []
    kept_titles = []
    for sel in selections:
        ct = (sel.get("content_type") or "").upper()
        name = sel.get("cluster_name", "")
        if ct == "HUB" or name in s.get("allow_duplicates", []):
            kept.append(sel)
            continue
        title = selection_title(sel)
        if s.get("block_speculative", True):
            low = title.lower()
            marker = next((m for m in SPECULATIVE_MARKERS if m in low), None)
            if marker:
                dropped.append((sel, f"출시 전 추측형 제목(\"{marker}\"): {title}"))
                continue
        hit = find_overlap(title, existing, s)
        if hit:
            ex, why = hit
            dropped.append((sel, f"기존 글과 중복({why}): {ex['title']}"))
            continue
        # 같은 배치 안 중복 (다른 클러스터가 같은 주제를 제안한 경우)
        dup_in_batch = None
        for other_title, other_name, other_ct in kept_titles:
            if other_name == name:
                continue            # 같은 클러스터의 다른 타입은 의도된 구성
            ow, cw = title_words(other_title), title_words(title)
            if _jaccard(ow, cw) >= s["title_jaccard"]:
                dup_in_batch = other_title
                break
        if dup_in_batch:
            dropped.append((sel, f"같은 배치의 다른 기획안과 중복: {dup_in_batch}"))
            continue
        kept.append(sel)
        kept_titles.append((title, name, ct))
    return kept, dropped


def build_existing_topics_block(existing=None, settings=None):
    """Step 2 프롬프트에 붙일 '이미 발행된 글' 블록."""
    s = settings or load_settings()
    existing = existing if existing is not None else load_existing_posts()
    titles = [e["title"] for e in existing][-s["max_titles_in_prompt"]:]
    lines = "\n".join(f"  - {t}" for t in titles)
    return f"""

[ALREADY PUBLISHED — 아래와 같은 주제는 제안하지 말 것]
이미 발행된 글 {len(titles)}편의 제목이다.
{lines}

[TOPIC RULES — 반드시 지킬 것]
1. 중복 기준은 "대상(기기/서비스) × 독자의 목적"이다.
   같은 대상이라도 목적이 다르면 허용: 설정 / 증상·에러별 문제 해결 / 호환성 /
   대안 / 업데이트로 바뀐 점 / 구매 판단. 목적까지 같으면 제안 금지.
2. 이미 출시된 제품에 대해 출시 전 추측형 제목 금지
   (anticipated, rumored, speculative, what to expect, envisioning).
3. 신기능·업데이트·롤아웃 소식(최근 14일 이내)은 우선 고려한다.
   각도는 "무엇이 바뀌었나 + 어떻게 쓰나".
4. 증상, 에러 코드, 경고 문구(LED 색, "Slow charger" 같은 문구)를 그대로 제목에 쓰는
   문제 해결형을 우선한다. 독자가 검색창에 치는 문장에 가깝게 쓴다.
5. 주제 폭을 넓힌다: 같은 제품 이야기를 여러 클러스터로 쪼개지 말고,
   서로 다른 제품/서비스/문제를 고르게 다룰 것.
"""


def related_posts(cluster_info, existing=None, settings=None):
    """글쓰기 프롬프트용 관련 글 [(title, url)] — 키워드 겹침 기준 상위 N개."""
    s = settings or load_settings()
    existing = existing if existing is not None else load_existing_posts()
    text = " ".join([
        cluster_info.get("cluster_name", ""),
        cluster_info.get("hub_keyword", ""),
        cluster_info.get("suggested_title", ""),
        " ".join(cluster_info.get("spoke_keywords", []) or []),
    ])
    qw = title_words(text)
    self_title = (cluster_info.get("suggested_title") or "").lower()
    scored = []
    for ex in existing:
        if not ex["url"] or ex["title"].lower() == self_title:
            continue
        ew = title_words(ex["title"])
        shared = qw & ew
        if len(shared) < 2:
            continue
        scored.append((len(shared) / max(len(ew), 1), len(shared), ex))
    scored.sort(key=lambda x: (-x[1], -x[0]))
    return [(e["title"], e["url"]) for _, _, e in scored[:s["max_related_links"]]]


def build_related_block(cluster_info, existing=None, settings=None):
    """write.py 프롬프트에 붙일 '관련 글' 블록 (실제 URL만)."""
    rel = related_posts(cluster_info, existing, settings)
    if not rel:
        return ("\n[RELATED ARTICLES]\n"
                "(관련된 기존 글 없음 — 내부 링크를 쓰지 말 것. "
                "[INTERNAL LINK: ...] 형태의 플레이스홀더도 쓰지 말 것.)\n")
    lines = "\n".join(f"  - [{t}]({u})" for t, u in rel)
    return f"""
[RELATED ARTICLES — 내부 링크는 아래 실제 글만 사용]
{lines}
- 가장 관련 있는 글 1~2개만 본문 또는 결론에서 위 마크다운 링크 그대로 사용한다.
- 맞지 않으면 링크를 쓰지 않는다. 목록에 없는 글을 만들어 내지 말 것.
- [INTERNAL LINK: ...] 형태의 플레이스홀더는 쓰지 말 것.
"""
