# =====================================================================
# 🌱 seed_inject.py — 개별 주제 추가 (Step 2-1)
# =====================================================================
# 역할: 주제 키워드를 받아서
#       1. posts.json에서 기존 발행 글 로드 (내부링크 컨텍스트)
#       2. Google News RSS로 관련 기사 수집
#       3. Gemini 기획 (기존 클러스터와 유기적 연동 포함)
#       4. content_pipeline.json에 append
#
# 사용법:
#   python seed_inject.py --topics "Android 16 desktop mode, Samsung DeX vs Android 16"
#   python seed_inject.py --topics "RTX 5090" --types "GUIDE,COMPARISON"
# =====================================================================

import os, re, sys, json, time, argparse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus
from collections import defaultdict

import requests

# ── 경로 설정 ──────────────────────────────────────────────────────
PIPELINE_FILE = "content_pipeline.json"
POSTS_FILE    = "posts.json"
CONFIG_FILE   = "config.json"
OUTPUT_DIR    = "research_data"

# ── Gemini 설정 ────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL     = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={{api_key}}"
)
MAX_RETRIES    = 3
RETRY_DELAY    = 10
JINA_BASE      = "https://r.jina.ai/"
JINA_MAX_CHARS = 2000

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

DEFAULT_TYPES = ["GUIDE", "COMPARISON", "EXPLAINER"]


# ── 유틸 ───────────────────────────────────────────────────────────

def get_week_tag():
    return datetime.now(timezone.utc).strftime("%Y-W%W")


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def load_json(path, default=None):
    try:
        return json.loads(open(path, encoding="utf-8").read())
    except FileNotFoundError:
        return default or {}


def save_pipeline(data):
    data["_last_updated"] = datetime.now(timezone.utc).isoformat()
    open(PIPELINE_FILE, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=2)
    )


# ── 기존 데이터 로드 ───────────────────────────────────────────────

def load_published_posts():
    """posts.json에서 발행된 글 전체 로드"""
    data  = load_json(POSTS_FILE, {"posts": []})
    posts = [p for p in data.get("posts", []) if p.get("status") == "live"]
    return posts


def build_cluster_map(posts):
    """클러스터별로 발행 글 그룹화"""
    clusters = defaultdict(list)
    for p in posts:
        hub = p.get("hub_cluster", "")
        if hub:
            clusters[hub].append(p)
    return dict(clusters)


def get_already_covered(pipeline):
    """이미 다룬 클러스터명 set 반환"""
    covered = set()
    for week, sels in pipeline.get("weekly_selections", {}).items():
        for sel in sels:
            if sel.get("status") != "rejected":
                covered.add(sel.get("cluster_name", "").lower())
    for name in pipeline.get("covered_clusters", {}).keys():
        covered.add(name.lower())
    return covered


def get_next_publish_order(pipeline, week_tag):
    """final/ + pipeline 기준 다음 publish_order 계산"""
    _final_dir = os.path.join("research_data", "write", "final")
    _max = 0
    if os.path.isdir(_final_dir):
        for f in Path(_final_dir).glob("*.md"):
            if f.name.startswith("review_report_"):
                continue
            prefix = f.name.split("_")[0]
            try:
                _max = max(_max, int(prefix))
            except ValueError:
                pass
    for sel in pipeline.get("weekly_selections", {}).get(week_tag, []):
        try:
            _max = max(_max, int(sel.get("publish_order", 0)))
        except (ValueError, TypeError):
            pass
    return _max + 1


# ── Google News RSS 수집 ───────────────────────────────────────────

def fetch_google_news_rss(topic, max_items=6):
    """Google News RSS에서 주제 관련 기사 수집"""
    url = (
        f"https://news.google.com/rss/search"
        f"?q={quote_plus(topic)}&hl=en-US&gl=US&ceid=US:en"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"    ⚠️ RSS {resp.status_code}")
            return []
        root  = ET.fromstring(resp.text)
        items = []
        for item in root.findall(".//item")[:max_items]:
            title  = item.findtext("title", "").strip()
            link   = item.findtext("link", "").strip()
            desc   = re.sub(r"<[^>]+>", "", item.findtext("description", ""))[:200]
            source = item.findtext("source", "").strip()
            pubdate = item.findtext("pubDate", "").strip()
            if title:
                items.append({
                    "title":   title,
                    "url":     link,
                    "desc":    desc.strip(),
                    "source":  source,
                    "pubdate": pubdate,
                })
        return items
    except Exception as e:
        print(f"    ⚠️ RSS 실패: {e}")
        return []


# ── Gemini 프롬프트 생성 ───────────────────────────────────────────

def build_prompt(topics_data, covered, pipeline, cluster_map, content_types, week_tag):
    """기존 발행 글과 유기적으로 연동된 Gemini 프롬프트 생성"""

    # ── 기존 발행 글 컨텍스트 ──
    published_section = ""
    for hub_name, posts in cluster_map.items():
        published_section += f"\n  [{hub_name} 클러스터]\n"
        for p in posts:
            published_section += (
                f"    - [{p['content_type']}] {p['title']}\n"
                f"      URL: {p['live_url']}\n"
                f"      Keywords: {', '.join(p.get('verified_keywords', []))}\n"
            )
    if not published_section:
        published_section = "  (없음)\n"

    # ── 이번 주 파이프라인 현황 ──
    current_week = pipeline.get("weekly_selections", {}).get(week_tag, [])
    current_section = ""
    for sel in current_week:
        if sel.get("status") == "candidate":
            current_section += f"  - [{sel['content_type']}] {sel['cluster_name']}\n"
    if not current_section:
        current_section = "  (없음)\n"

    # ── 주제별 RSS 수집 데이터 ──
    topics_section = ""
    for topic, articles in topics_data.items():
        topics_section += f"\n### 주제: {topic}\n"
        if articles:
            for a in articles:
                topics_section += f"  - [{a['source']}] {a['title']}\n"
                if a.get("desc"):
                    topics_section += f"    {a['desc'][:120]}\n"
        else:
            topics_section += "  (기사 없음 — 키워드만으로 기획)\n"

    # ── content_type 지시 ──
    types_str = ", ".join(content_types) if content_types else "GUIDE, COMPARISON, EXPLAINER"

    prompt = f"""You are a senior content strategist for Frontbuffer Editorial, a tech and gaming blog targeting English-speaking readers.

## YOUR TASK
The editor has manually selected topics to add to the content pipeline.
Generate ONE cluster entry per topic. Each cluster must:
1. Be evergreen (valuable beyond this week's news cycle)
2. Connect organically to existing published articles where possible
3. Not duplicate any already-covered cluster

## MANUALLY SELECTED TOPICS WITH NEWS CONTEXT
{topics_section}

## ALREADY PUBLISHED ARTICLES (for internal linking context)
Use these to:
- Identify natural internal link opportunities in spoke_keywords
- Avoid duplicating what's already covered
- Extend existing cluster themes where relevant
{published_section}

## CURRENTLY IN PIPELINE THIS WEEK (do not duplicate)
{current_section}

## ALREADY COVERED CLUSTERS (do not repeat)
{chr(10).join(f"  - {c}" for c in sorted(covered)[:40]) or "  (none)"}

## CONTENT TYPES TO USE
Choose the best fit per topic from: {types_str}
- GUIDE: How-to, step-by-step instructions
- COMPARISON: Side-by-side analysis of 2-3 options
- EXPLAINER: What/why/how concept explanation
- LISTICLE: Ranked or categorized list

## INTERNAL LINKING RULES
- In spoke_keywords, include 1-2 keywords that naturally connect to existing published articles
- Example: if topic is "Android 16 desktop mode" and we have published "Samsung DeX" articles,
  include "samsung dex vs android 16 desktop" as a spoke keyword
- This enables publish_one.py to automatically inject internal links

## OUTPUT FORMAT
Return ONLY a valid JSON array. No markdown fences. No explanation.

[
  {{
    "cluster_name": "Android 16 Desktop Mode",
    "content_type": "GUIDE",
    "hub_keyword": "Android 16 desktop mode",
    "spoke_keywords": [
      "how to use android 16 desktop mode",
      "android 16 connected display setup",
      "android 16 desktop mode supported phones",
      "samsung dex vs android 16 desktop"
    ],
    "internal_link_targets": [
      "Samsung Health vs Google Health Connect Feature Comparison",
      "How to Optimize Cover Screen Apps on Galaxy Z Flip 8"
    ],
    "rationale": "Android 16 desktop mode is GA since March 2026, high search intent for setup guides, evergreen as feature matures",
    "data_grade": "A",
    "trends_pattern": "RISING",
    "folder": "",
    "source": "seed_inject",
    "week_tag": "{week_tag}"
  }}
]

IMPORTANT:
- internal_link_targets: list of EXACT titles from the published articles above that this new article should link to
- Leave internal_link_targets empty [] if no natural connection exists
- folder: always empty string ""
- data_grade: always "A" (manually selected = trusted)
"""
    return prompt


# ── Gemini API 호출 ────────────────────────────────────────────────

def call_gemini(prompt_text):
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY 없음")
        sys.exit(1)

    url     = GEMINI_URL.format(api_key=GEMINI_API_KEY)
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "temperature":     0.3,
            "maxOutputTokens": 4096,
        }
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"  🤖 Gemini 호출... (시도 {attempt}/{MAX_RETRIES})")
            resp = requests.post(url, json=payload, timeout=120)
            if resp.status_code == 200:
                parts = (resp.json()
                         .get("candidates", [{}])[0]
                         .get("content", {})
                         .get("parts", [{}]))
                text = "".join(p.get("text", "") for p in parts).strip()
                if text:
                    return text
                print("  ⚠️ 응답 비어있음")
            elif resp.status_code == 429:
                print(f"  ⚠️ Rate limit — {RETRY_DELAY}초 대기")
                time.sleep(RETRY_DELAY)
            else:
                print(f"  ❌ API 오류 {resp.status_code}: {resp.text[:200]}")
                break
        except requests.exceptions.Timeout:
            print(f"  ⚠️ 타임아웃 — {RETRY_DELAY}초 대기")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"  ❌ 예외: {e}")
            break
    return None


def parse_json_response(text):
    text = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON 파싱 실패: {e}")
        return []


# ── 메인 ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Step 2-1: 개별 주제 추가")
    parser.add_argument("topics", nargs="*", help="주제 (위치 인자)")
    parser.add_argument("--topics", dest="topics_str", default="",
                        help="콤마 구분 주제")
    parser.add_argument("--types",  default="",
                        help="content_type (예: GUIDE,COMPARISON)")
    parser.add_argument("--week",   default=None)
    args = parser.parse_args()

    # 주제 파싱
    topics = list(args.topics or [])
    if args.topics_str:
        topics += [t.strip() for t in args.topics_str.split(",") if t.strip()]
    topics = list(dict.fromkeys(topics))

    if not topics:
        print("❌ 주제를 입력하세요.")
        print("   예: python seed_inject.py --topics 'Android 16 desktop mode'")
        sys.exit(1)

    content_types = (
        [t.strip().upper() for t in args.types.split(",") if t.strip()]
        if args.types else DEFAULT_TYPES
    )
    week_tag = args.week or get_week_tag()

    print("=" * 60)
    print("🌱 Step 2-1: 개별 주제 추가")
    print("=" * 60)
    print(f"  주차: {week_tag}")
    print(f"  주제: {topics}")
    print(f"  타입: {content_types}")

    # 데이터 로드
    pipeline    = load_json(PIPELINE_FILE, {"weekly_selections": {}, "covered_clusters": {}, "published": []})
    posts       = load_published_posts()
    cluster_map = build_cluster_map(posts)
    covered     = get_already_covered(pipeline)

    print(f"  발행된 글: {len(posts)}편 / {len(cluster_map)}개 클러스터")
    print(f"  기존 커버: {len(covered)}개 클러스터")

    # ── Step 1: Google News RSS 수집 ──
    print(f"\n{'─'*40}")
    print("📰 Google News RSS 수집")
    topics_data = {}
    for topic in topics:
        print(f"  🔍 '{topic}' ...")
        articles = fetch_google_news_rss(topic, max_items=6)
        topics_data[topic] = articles
        print(f"    → {len(articles)}개 기사")
        for a in articles[:2]:
            print(f"      [{a['source']}] {a['title'][:70]}")
        time.sleep(1)

    # ── Step 2: Gemini 기획 ──
    print(f"\n{'─'*40}")
    print("🤖 Gemini 기획 생성")
    prompt = build_prompt(topics_data, covered, pipeline, cluster_map, content_types, week_tag)

    # 프롬프트 저장 (디버깅용)
    prompt_dir  = os.path.join(OUTPUT_DIR, "weekly", week_tag)
    os.makedirs(prompt_dir, exist_ok=True)
    ts          = int(time.time())
    prompt_path = os.path.join(prompt_dir, f"seed_prompt_{ts}.txt")
    open(prompt_path, "w", encoding="utf-8").write(prompt)
    print(f"  📄 프롬프트: {prompt_path}")

    response = call_gemini(prompt)
    if not response:
        print("❌ Gemini 응답 없음")
        sys.exit(1)

    # ── Step 3: JSON 파싱 ──
    selections = parse_json_response(response)
    if not selections:
        raw_path = os.path.join(prompt_dir, f"seed_raw_{ts}.txt")
        open(raw_path, "w", encoding="utf-8").write(response)
        print(f"❌ 파싱 실패 — 원문: {raw_path}")
        sys.exit(1)

    print(f"  ✅ {len(selections)}개 기획안 파싱")

    # ── Step 4: 중복 체크 + publish_order + pipeline append ──
    next_order = get_next_publish_order(pipeline, week_tag)
    now        = datetime.now(timezone.utc)
    added      = []

    for sel in selections:
        name = sel.get("cluster_name", "").strip()
        if not name:
            continue
        if name.lower() in covered:
            print(f"  ⏭️  중복 스킵: {name}")
            continue

        # 필수 필드 보완
        sel.setdefault("content_type",   "GUIDE")
        sel.setdefault("data_grade",     "A")
        sel.setdefault("trends_pattern", "STABLE")
        sel.setdefault("hub_keyword",    slugify(name))
        sel.setdefault("spoke_keywords", [])
        sel.setdefault("internal_link_targets", [])
        sel.setdefault("folder",         "")
        sel["publish_order"] = next_order
        sel["status"]        = "candidate"
        sel["week_tag"]      = week_tag
        sel["selected_at"]   = now.isoformat()
        sel["source"]        = "seed_inject"

        next_order += 1
        added.append(sel)

        # 내부링크 타겟 출력
        link_targets = sel.get("internal_link_targets", [])
        print(f"  ✅ [{sel['publish_order']:03d}] {name} [{sel['content_type']}]")
        if link_targets:
            print(f"       → 내부링크 타겟: {link_targets}")

    if not added:
        print("⚠️  추가된 클러스터 없음 (모두 중복)")
        sys.exit(0)

    # pipeline에 append
    week_sels = pipeline.setdefault("weekly_selections", {}).setdefault(week_tag, [])
    week_sels.extend(added)
    save_pipeline(pipeline)

    print(f"\n{'='*60}")
    print(f"✅ content_pipeline.json 업데이트: {len(added)}개 추가")
    print(f"   다음 단계: Step 3 트리거 → 글 생성")
    print("=" * 60)


if __name__ == "__main__":
    main()
