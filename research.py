# =====================================================================
# 📊 주간 리서치 스캔 (research.py) — v4
# =====================================================================
# 목적: 에버그린 콘텐츠 기회 발굴 (발행 아님)
# 실행: python research.py  (수동, 주 1회, 비용 발생 없음)
# 설정: config.json
# 출력:
#   research_data/raw_research_log_YYYY-WW.json  (원시 데이터)
#   research_data/manual_report_YYYY-WW.md       (AI 분석용 리포트)
# =====================================================================

import os
import re
import sys
import json
import time
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# Windows 한국어 환경에서 이모지/유니코드 출력 보장
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests
from bs4 import BeautifulSoup

# ── 설정 로드 ──
with open("config.json", encoding="utf-8") as f:
    CFG = json.load(f)

OUTPUT_DIR          = CFG["output_dir"]
WEEKLY_DIR          = os.path.join(OUTPUT_DIR, "weekly")  # 주차별 파일 저장
COLLECT_WINDOW_DAYS = CFG["collect"]["window_days"]
MAX_PER_SOURCE      = CFG["collect"]["max_items_per_source"]
REDDIT_ENABLED      = CFG["collect"]["reddit_enabled"]
REDDIT_DELAY        = CFG["collect"]["reddit_delay_seconds"]
NEWS_SOURCES        = CFG["news_rss_sources"]
COMMUNITY_SOURCES   = CFG["community_rss_sources"]
REDDIT_SUBS         = CFG["reddit_subs"]
FREQ_CFG            = CFG["frequency"]

COLLECT_WINDOW_HOURS = COLLECT_WINDOW_DAYS * 24

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# ── 쇼핑/딜 필터 ──
_SHOPPING_RE = re.compile(
    r"\bsave\s+\d"
    r"|\d+%\s*off\b"
    r"|\boff\s+the\b"
    r"|\bdrops?\s+to\s+\$"
    r"|\bfor\s+\$\d"
    r"|\bdeal\b"
    r"|\bdeals\b"
    r"|\brefurb\b"
    r"|\boutlet\b"
    r"|\bdiscount\b"
    r"|\bcoupon\b"
    r"|\bpromo\b"
    r"|\bshipped\b",
    re.IGNORECASE,
)

def is_shopping(title):
    return bool(_SHOPPING_RE.search(title))

# ── 불용어 ──
STOPWORDS = {
    'the','a','an','is','are','was','were','be','been','to','of',
    'in','for','on','with','at','by','from','and','or','but','as',
    'it','its','this','that','new','now','will','has','have','had',
    'you','your','more','get','gets','how','why','what','when','who',
    'can','could','should','would','may','might','just','about','after',
    'before','over','under','into','out','up','down','not','all','some',
    'says','said','report','reports','update','news','here','best',
    'first','last','year','years','week','day','today','still','also',
    'reportedly','than','off','make','even','later','like','back',
    'made','set','drops','finally','latest','via','after','i',
}


# =====================================================================
# [1단계] 수집
# =====================================================================

def _parse_pubdate(text):
    try:
        return parsedate_to_datetime(text)
    except Exception:
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except Exception:
            return None


def _fetch_rss(sources, label="소스"):
    """공통 RSS 수집 함수."""
    now_utc = datetime.now(timezone.utc)
    items   = []
    skipped = 0

    for src in sources:
        try:
            resp = requests.get(src["url"], headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"  ⚠️ {src['source']}: HTTP {resp.status_code}")
                continue

            soup    = BeautifulSoup(resp.content, "xml")
            entries = soup.find_all("item") or soup.find_all("entry")
            count   = 0

            for entry in entries[:MAX_PER_SOURCE]:
                title_tag = entry.find("title")
                title     = title_tag.text.strip() if title_tag else ""
                if not title:
                    continue
                if is_shopping(title):
                    skipped += 1
                    continue

                link_tag = entry.find("link")
                link     = ""
                if link_tag:
                    link = link_tag.get("href") or (link_tag.text or "").strip()

                pub_tag = (entry.find("pubDate") or
                           entry.find("published") or
                           entry.find("updated"))
                pub_dt  = _parse_pubdate(pub_tag.text.strip()) if pub_tag else None
                if pub_dt:
                    hours_old = (now_utc - pub_dt).total_seconds() / 3600
                    if hours_old > COLLECT_WINDOW_HOURS:
                        continue

                items.append({
                    "title":           title,
                    "link":            link,
                    "source":          src["source"],
                    "source_category": src.get("category", "general"),
                    "kind":            src.get("category", "general"),
                    "pub_date":        pub_dt.isoformat() if pub_dt else None,
                })
                count += 1

            print(f"  • {src['source']}: {count}개")
        except Exception as e:
            print(f"  ⚠️ {src['source']} 실패: {e}")

    if skipped:
        print(f"  → 쇼핑/딜 글 {skipped}개 필터링됨")
    return items


def collect_news():
    print(f"📰 [1/3] 뉴스 RSS 수집 중... ({len(NEWS_SOURCES)}개 소스, 최대 {MAX_PER_SOURCE}개/소스)")
    return _fetch_rss(NEWS_SOURCES, "뉴스")


def collect_community():
    print(f"🌐 [2/3] 커뮤니티 RSS 수집 중... (Hacker News, Google Trends 등)")
    return _fetch_rss(COMMUNITY_SOURCES, "커뮤니티")


def collect_reddit():
    if not REDDIT_ENABLED:
        print("👥 [3/3] Reddit 수집 비활성화 (config: reddit_enabled=false)")
        return []

    print("👥 [3/3] Reddit RSS 수집 중...")
    now_utc = datetime.now(timezone.utc)
    items   = []

    for sub in REDDIT_SUBS:
        try:
            url  = f"https://www.reddit.com/r/{sub}/.rss"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code in (403, 429):
                print(f"  ⚠️ r/{sub}: HTTP {resp.status_code} — 건너뜀")
                time.sleep(REDDIT_DELAY)
                continue
            if resp.status_code != 200:
                print(f"  ⚠️ r/{sub}: HTTP {resp.status_code}")
                continue

            soup    = BeautifulSoup(resp.content, "xml")
            entries = soup.find_all("entry")
            count   = 0

            for entry in entries[:MAX_PER_SOURCE]:
                title_tag = entry.find("title")
                title     = title_tag.text.strip() if title_tag else ""
                if not title or is_shopping(title):
                    continue
                if any(t in title.lower() for t in ["[mod]","[announcement]","weekly","megathread"]):
                    continue

                link_tag = entry.find("link")
                link     = link_tag.get("href", "") if link_tag else ""

                updated_tag = entry.find("updated")
                pub_dt      = _parse_pubdate(updated_tag.text.strip()) if updated_tag else None
                if pub_dt:
                    hours_old = (now_utc - pub_dt).total_seconds() / 3600
                    if hours_old > COLLECT_WINDOW_HOURS:
                        continue

                items.append({
                    "title":           title,
                    "link":            link,
                    "source":          f"r/{sub}",
                    "source_category": "reddit",
                    "kind":            "reddit",
                    "pub_date":        pub_dt.isoformat() if pub_dt else None,
                })
                count += 1

            print(f"  • r/{sub}: {count}개")
            time.sleep(REDDIT_DELAY)
        except Exception as e:
            print(f"  ⚠️ r/{sub} 실패: {e}")

    return items


# =====================================================================
# [2단계] 키워드 빈도 집계
# =====================================================================

def extract_keywords(title):
    words = re.sub(r"[^\w\s'-]", " ", title.lower()).split()
    out   = []
    for w in words:
        w = w.strip("'-")
        if not w or w in STOPWORDS or len(w) <= 2 or w.isdigit():
            continue
        out.append(w)
    return out


def build_frequency(items):
    print("🔢 키워드 빈도 집계 중...")
    uni = Counter()
    bi  = Counter()
    for it in items:
        kws = extract_keywords(it["title"])
        uni.update(kws)
        bi.update(f"{a} {b}" for a, b in zip(kws, kws[1:]))

    top_uni = [(w, c) for w, c in uni.most_common(FREQ_CFG["top_words"])
               if c >= FREQ_CFG["min_word_count"]]
    top_bi  = [(w, c) for w, c in bi.most_common(FREQ_CFG["top_bigrams"])
               if c >= FREQ_CFG["min_bigram_count"]]
    print(f"  • 단어 {len(top_uni)}개 / 2단어 조합 {len(top_bi)}개")
    return top_uni, top_bi


# =====================================================================
# [3단계] 리포트 생성 (AI 호출 없음 — 수동 붙여넣기용)
# =====================================================================

KIND_LABELS = {
    "tech":    "뉴스 (테크)",
    "gaming":  "뉴스 (게이밍)",
    "trends":  "Google Trends 급상승",
    "reddit":  "Reddit",
    "general": "커뮤니티",
}

def _trim_title(title, max_len=60):
    """제목을 max_len자로 트리밍 (중간 잘림 방지 — 단어 단위)."""
    if len(title) <= max_len:
        return title
    return title[:max_len].rsplit(" ", 1)[0].rstrip(",-") + "..."


def load_trends_opportunities():
    """
    trends_analyzer.py가 저장한 최신 분석 결과에서
    콘텐츠 기회 키워드를 로드합니다.
    """
    trends_dir = os.path.join(OUTPUT_DIR, "trends")
    if not os.path.exists(trends_dir):
        return ""

    analysis_files = sorted(
        [f for f in os.listdir(trends_dir) if f.startswith("analysis_") and f.endswith(".json")],
        reverse=True
    )[:5]  # 최근 5개

    if not analysis_files:
        return ""

    lines = ["TRENDS ANALYSIS (from recent Google Trends CSV downloads):"]
    for fname in analysis_files:
        try:
            with open(os.path.join(trends_dir, fname), encoding="utf-8") as f:
                data = json.load(f)
            kw      = data.get("keyword", "")
            pattern = data.get("pattern", "UNKNOWN")
            opps    = [o["query"] for o in data.get("opportunities", [])[:5]]
            opps_str = ", ".join(f'"{q}"' for q in opps) if opps else "none"
            lines.append(f"- {kw}: {pattern} | opportunity queries: {opps_str}")
        except Exception:
            pass

    return "\n".join(lines) if len(lines) > 1 else ""


def build_ai_prompt(top_uni, top_bi, items, week_tag):
    """
    AI에게 전달할 순수 프롬프트 파일 생성.
    - 제목 55자 트리밍 적용
    - covered_clusters 주입 (중복 방지)
    - trends 기회 키워드 주입 (롱테일 유도)
    - 과대해석 방지 규칙
    - 허브+스포크 구조 요청
    - prompt_YYYY-WW.txt 로 저장
    """
    # covered_clusters 요약 + 이미 선택된 기획안 목록 (중복 제안 방지)
    try:
        from pipeline import build_covered_summary, load_pipeline
        covered_section = build_covered_summary()
        data = load_pipeline()
        selected_names = []
        for week_sels in data.get("weekly_selections", {}).values():
            for s in week_sels:
                name = s.get("cluster_name", "")
                if name and name not in selected_names:
                    selected_names.append(name)
        if selected_names:
            covered_section += "\n\nALREADY SELECTED THIS CYCLE (do NOT re-propose these):\n"
            covered_section += "\n".join(f"  - {n}" for n in selected_names)
    except Exception:
        covered_section = ""

    # trends 기회 키워드 로드
    trends_section = load_trends_opportunities()

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    by_kind = {}
    for it in items:
        by_kind.setdefault(it["kind"], []).append(it)

    # 제목 트리밍 + 소스 태그 제거
    title_sections = ""
    for kind, label in KIND_LABELS.items():
        subset = by_kind.get(kind, [])
        if subset:
            lines = "\n".join(
                f"  - {_trim_title(i['title'], 55)}"
                for i in subset
            )
            title_sections += f"\n[{label}]\n{lines}\n"

    kw_uni_lines = "\n".join(f"  {w} ({c}회)" for w, c in top_uni)
    kw_bi_lines  = "\n".join(f"  {p} ({c}회)" for p, c in top_bi)

    # 선택적 섹션 블록
    covered_block = f"\n{covered_section}\n\n" if covered_section else ""
    trends_block  = f"\n{trends_section}\n\n" if trends_section else ""

    prompt = f"""You are a content strategist for LIFO-LIKE Editorial, an independent tech/gaming media brand.
Your goal is to find EVERGREEN content opportunities — especially LONG-TAIL keywords
where a new blog can realistically rank on Google page 1.

CORE PRINCIPLE:
- Evergreen = people will still search this in 6+ months
- News frequency ≠ search demand. High mentions ≠ high search volume.
- NEW BLOG REALITY: Domain authority is near zero. Short-tail competitive keywords
  (e.g. "Galaxy Z Fold 8 review") are dominated by The Verge, Tom's Guide, GSMArena.
  We cannot rank for these in the short term.
- LONG-TAIL STRATEGY: Target 3-5 word specific queries with lower competition.
  Examples of good long-tail:
    "galaxy z fold 8 vs fold 7 hinge durability test"
    "steam deck windows 11 audio driver not working fix"
    "pixel 11 vs pixel 10 low light camera comparison"
- content_type priority: COMPARISON > GUIDE > EXPLAINER > LISTICLE

EARLY-STAGE TIMING POLICY (CRITICAL):
This blog is in its early stage with near-zero domain authority. Therefore:
- Do NOT propose PRE-LAUNCH clusters (topics whose value depends on an
  unreleased, rumored, or unannounced product).
- Rumor/leak-based topics (e.g. "leaked specs", "expected price") are EXCLUDED.
- timing must be "NOW" or "WAIT" only. Never output "PRE-LAUNCH".
- Products already RELEASED with official specs/docs = "NOW" (preferred).
- Products announced but specifics unclear = "WAIT" (will revisit later).

VERIFIABILITY RULE (CRITICAL — this pipeline has NO hands-on access):
Our writers verify facts through public web sources only. They cannot play games,
test hardware, or use products directly. Therefore:
- ONLY suggest topics whose facts can be verified from public web sources
  (official documentation, spec sheets, published articles, Wikipedia)
- EXCLUDE topics requiring first-hand experience:
  ✗ Game walkthroughs/quest guides for NEW indie games
    (quest triggers, item locations — unverifiable without playing)
  ✗ Hands-on reviews, "we tested" content
  ✗ Benchmark comparisons requiring actual measurement
- GOOD verifiable examples:
  ✓ Spec/price comparisons from official announcements
  ✓ How-to guides based on official documentation (drivers, settings, features)
  ✓ Explainers of announced technology
- Each cluster MUST include: "verifiability": "HIGH / MEDIUM / LOW"
  HIGH   = official docs/specs exist publicly
  MEDIUM = multiple secondary sources cover the facts
  LOW    = requires first-hand experience → DO NOT INCLUDE THESE AT ALL
{covered_block}{trends_block}INPUT DATA (collected {now_str}, {len(items)} items, shopping/deal posts removed):

[단어 빈도 Top]
{kw_uni_lines}

[2단어 조합 빈도 Top]
{kw_bi_lines}
{title_sections}
TASKS:
1. Identify 3-5 HUB CLUSTERS from the news data.
   News headlines = signal for WHICH topics are hot right now.
   News content itself = NOT used directly in articles.
   A hub cluster = one broad topic area with 3-4 evergreen rankable angles.

2. For each hub cluster, generate 3-4 EVERGREEN SPOKES:
   - ALL spokes must be 100% evergreen (searchable 6+ months from now)
   - Use the news as a discovery signal only — do NOT write news articles
   - Re-frame news triggers into timeless search queries:
       ✗ "How to Fix Steam Machine Red Light Bug" (patch-dependent)
       ✓ "How to Troubleshoot Steam Machine Overheating Issues" (timeless)
       ✗ "Samsung Health Deleting Data Policy 2026" (policy may change)
       ✓ "How to Backup Samsung Health Data Before Switching Phones" (always relevant)
   - Goal: 3-4 spokes per hub so hub article can be written after 2+ spokes published

3. Output each spoke as a SEPARATE JSON object in the array.
   Each object = one article to write.
   Total output: 9-20 spokes across 3-5 hubs.

EVERGREEN SPOKE RULES:
- Must remain valid and searchable 6+ months from now regardless of patches/updates
- Must pass all VERIFIABILITY and GAMING EXCLUSION rules
- Prefer COMPARISON > GUIDE > EXPLAINER > LISTICLE
- Timeless question formats work best:
    "How to [do X] with [Product]"
    "[Product A] vs [Product B]: [specific angle]"
    "What is [Feature] in [Product] and How Does It Work"
    "Best [Product] Settings for [Use Case]"

EXAMPLE OUTPUT (Steam Machine hub — 4 evergreen spokes):
  Spoke 1: "How to Troubleshoot Steam Machine Overheating and Warning Lights"
  Spoke 2: "Steam Machine vs Steam Deck: Performance and Price Comparison"
  Spoke 3: "How to Check Steam Machine Verified Compatibility for Your Games"
  Spoke 4: "Steam Machine Setup Guide: Connecting to TV and External Displays"
  → All 4 share parent_hub: "Steam Machine"
  → After 2 spokes published → hub article "Steam Machine Complete Guide" written

OUTPUT FORMAT — respond ONLY with a raw JSON array, no markdown fences, no other text:
[
  {{
    "cluster_name": "...",
    "content_type": "COMPARISON",
    "suggested_title": "...(long-tail, 5-10 words, specific, timeless)",
    "hub_keyword": "...(1-3 words, broader)",
    "parent_hub": "...(2-3 words, same for all spokes in same hub cluster)",
    "spoke_keywords": ["specific long-tail 1", "specific long-tail 2"],
    "evergreen_score": 85,
    "competition_level": "LOW / MEDIUM / HIGH",
    "affiliate_potential": "HIGH / MEDIUM / LOW",
    "timing": "NOW / WAIT",
    "verifiability": "HIGH / MEDIUM",
    "trends_queries": ["...", "..."],
    "reasoning": "1-2 sentences in Korean — why this is evergreen and rankable"
  }}
]

CRITICAL RULES:
- timing field is MANDATORY — never omit it. PRE-LAUNCH is FORBIDDEN in output
- competition_level is MANDATORY — never omit it
- verifiability is MANDATORY — LOW verifiability clusters must NOT appear in output
- parent_hub is MANDATORY — must be a broad 2-3 word keyword suitable for Google Trends/KP search
  Examples: "Steam Machine" not "Steam Machine Verified Medals"
            "Samsung Health" not "Samsung Health Data Deletion"
            "Chrome Extensions" not "Chrome Manifest V2 Transition"
- ANTI-HALLUCINATION: spoke titles and keywords must be verifiable, not invented
- Prefer LOW/MEDIUM competition clusters — HIGH competition = new blog can't rank
- spoke_keywords must be 4+ words, specific, question or problem-solving format
- If COVERED TOPICS exist: suggest different content_type for same cluster
- evergreen_score above 70 = serious candidate
- Output raw JSON only — no explanation, no preamble

GAMING CONTENT EXCLUSION RULES (apply strictly):
These gaming topics are NOT evergreen and must be EXCLUDED:
  ✗ In-game keybindings, control settings, UI options
    (patch updates change these constantly — content expires within weeks)
  ✗ Early Access or actively-developed games' mechanics/tips
    (Palworld, Star Citizen etc. — update cadence invalidates content)
  ✗ Game walkthroughs, item locations, quest guides
    (requires first-hand play — already covered by VERIFIABILITY RULE)
  ✗ Vague multi-game guides without a specific game title
    (e.g. "Mac Music App Guides", "Open Source Gaming Tips")
  ✗ Game-specific trivial settings findable in-game menus
    (e.g. "how to change hold F in Palworld")

Gaming topics that ARE acceptable:
  ✓ Mod installation guides based on Nexus Mods / official mod tools
  ✓ Cross-platform compatibility (Steam Deck verified, OS support)
  ✓ Spec/hardware comparison for gaming peripherals (official specs only)
  ✓ DRM, launcher, or account management issues with public documentation

TOPIC SPECIFICITY RULE:
- suggested_title must reference a SPECIFIC product, game, or feature name
  ✗ "Open Source Mac Music App Guides" — no specific app named
  ✗ "Android Security Tips" — too broad
  ✓ "How to Remove Yellow Filter in AC Black Flag Resynced"
  ✓ "How to Stop Samsung Health Deleting Your Data Automatically"
"""

    return prompt


def build_human_report(top_uni, top_bi, items, week_tag, prompt_filename):
    """
    사람이 읽는 리포트 생성.
    - 원본 링크 포함 (직접 확인용)
    - AI 프롬프트 블록 없음 (별도 파일로 분리됨)
    - [D] 기획안 입력란 포함
    - manual_report_YYYY-WW.md 로 저장
    """
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    by_kind = {}
    for it in items:
        by_kind.setdefault(it["kind"], []).append(it)

    total         = len(items)
    count_by_kind = {k: len(v) for k, v in by_kind.items()}

    lines = [
        f"# 📦 주간 리서치 리포트 — {week_tag}",
        f"> 수집: {now_str}",
        f"> 합계 {total}건 | " + " / ".join(
            f"{KIND_LABELS.get(k, k)} {v}건" for k, v in count_by_kind.items()
        ),
        f"> 쇼핑/딜 글은 수집 단계에서 이미 제외됨",
        f"> 소스: {', '.join(s['source'] for s in NEWS_SOURCES + COMMUNITY_SOURCES)}",
        "",
        "---",
        "",
        "## 📋 사용 방법",
        "",
        f"1. `{prompt_filename}` 파일을 AI 웹에 첨부하거나 내용을 붙여넣기",
        "2. JSON 결과를 받아서 **[D] 결과 입력란**에 요약 기입",
        "3. `timing: NOW / PRE-LAUNCH` 항목만 추려서 2~3개 선택",
        "4. `trends.google.com`에서 제안 검색어 수동 확인",
        "5. 최종 선택 → 발행 파이프라인으로",
        "",
        "---",
        "",
        "## [C] 원본 제목 전체 (링크 포함 — 직접 확인용)",
        "",
    ]

    for kind, label in KIND_LABELS.items():
        subset = by_kind.get(kind, [])
        if subset:
            lines += [f"### {label}", ""]
            for it in subset:
                lines.append(f"- [{it['title']}]({it['link']}) — {it['source']}")
            lines.append("")

    # ── Trends 검색 추천 섹션 ──────────────────────────────────────
    NEWS_WORDS = {
        "world", "cup", "final", "hints", "answers", "monday", "sunday",
        "july", "watch", "free", "live", "streams", "channels", "review",
        "today", "week", "this", "just", "new", "latest", "breaking",
        "game", "games", "director", "studio", "next", "every", "around",
    }
    evergreen_bi = [
        (p, c) for p, c in top_bi
        if not any(w in NEWS_WORDS for w in p.lower().split())
        and c >= 3
    ][:10]
    evergreen_uni = [
        (w, c) for w, c in top_uni
        if w not in NEWS_WORDS and len(w) > 4 and c >= 5
    ][:8]

    trends_folder_base = f"research_data/trends/{week_tag}"
    trends_lines = [
        "---",
        "",
        "## 🔍 Google Trends / Keyword Planner 검색 추천",
        "",
        "> 아래 키워드를 Google Trends에서 검색 후 CSV를 해당 폴더에 넣으세요.",
        f"> 폴더 경로: `{trends_folder_base}/{{폴더명}}/`",
        "",
        "### 추천 허브 키워드 (2단어 조합 빈도 기준)",
        "",
        "| 순위 | 키워드 | 빈도 | Trends 링크 | 폴더명 |",
        "|---|---|---|---|---|",
    ]
    for i, (phrase, count) in enumerate(evergreen_bi, 1):
        folder_name = f"{i:02d}-{phrase.replace(' ', '-')}"
        url = "https://trends.google.com/trends/explore?q=" + phrase.replace(" ", "+") + "&geo=US"
        trends_lines.append(
            f"| {i} | **{phrase}** | {count}회 | [Trends 검색]({url}) | `{folder_name}/` |"
        )

    trends_lines += [
        "",
        "### 단일 키워드 보조 참고",
        "",
        "| 키워드 | 빈도 |",
        "|---|---|",
    ]
    for w, c in evergreen_uni:
        trends_lines.append(f"| {w} | {c}회 |")

    trends_lines += [
        "",
        "### Trends CSV 넣는 방법",
        "",
        "```",
        "1. trends.google.com → 키워드 검색 → 다운로드(↓)",
        "   파일명 그대로 올리면 돼요 (이름 변경 불필요)",
        "   - multiTimeline.csv      ← 시계열 데이터",
        "   - relatedQueries.csv     ← 연관검색어",
        "   - relatedEntities.csv    ← 연관 주제",
        "   (geoMap.csv는 무시됨)",
        "",
        f"2. GitHub → {trends_folder_base}/{{폴더명}}/ 에 업로드",
        "",
        "3. KP CSV (선택): Keyword Planner → 키워드 아이디어 → 다운로드",
        f"   → {trends_folder_base}/ 루트에 업로드 (폴더 안 아님)",
        "```",
        "",
    ]

    # ── KP 입력용 키워드 복사 섹션 ──────────────────────────────────
    # hub_keyword 기준으로 중복 제거 후 KP 검색용 키워드 목록 생성
    kp_keywords_for_copy = list(dict.fromkeys(
        phrase for phrase, _ in evergreen_bi
    ))
    # 단일 키워드도 추가 (에버그린 단어 중 4자 이상)
    for w, _ in evergreen_uni:
        if w not in " ".join(kp_keywords_for_copy):
            kp_keywords_for_copy.append(w)

    trends_lines_kp = [
        "---",
        "",
        "## 📋 Keyword Planner 입력용 키워드",
        "",
        "> 아래 키워드를 **전체 복사**해서 Google Ads Keyword Planner에 붙여넣기하세요.",
        f"> 결과 CSV → `{trends_folder_base}/` 루트에 업로드 (파일명에 'keyword' 포함 필수)",
        "",
        "```",
    ]
    for kw in kp_keywords_for_copy:
        trends_lines_kp.append(kw)
    trends_lines_kp += [
        "```",
        "",
        "> 💡 **KP 검색 팁**: 넓은 hub 키워드로 검색해야 롱테일 발굴 가능해요.",
        "> LOW 경쟁 + 월 100회 이상 키워드만 자동으로 채택돼요.",
        "",
    ]
    lines += trends_lines
    lines += trends_lines_kp

    lines += [
        "---",
        "",
        "## [D] AI 분석 결과 입력란",
        "",
        "> AI JSON 결과를 받은 후 핵심 내용을 아래 표에 요약하세요.",
        "> `timing=NOW/PRE-LAUNCH` 항목 우선 선택.",
        "",
        "| # | 클러스터명 | 유형 | 제안 제목 | 에버그린 | 어필리에이트 | timing | Trends 검색어 |",
        "|---|---|---|---|---|---|---|---|",
        "| 1 | | | | | | | |",
        "| 2 | | | | | | | |",
        "| 3 | | | | | | | |",
        "| 4 | | | | | | | |",
        "| 5 | | | | | | | |",
        "",
        "**최종 선택 (2~3개):**",
        "",
        "**Trends 확인 결과:**",
        "",
    ]

    # ── Trends 폴더 자동 생성 ──────────────────────────────────────
    # manual_report.md 생성 시 추천 키워드 기반 폴더를 미리 만들어둠
    # 사람이 GitHub에서 바로 CSV를 업로드할 수 있도록
    trends_week_dir = os.path.join("research_data", "trends", week_tag)
    created_folders = []
    try:
        os.makedirs(trends_week_dir, exist_ok=True)
        for i, (phrase, _) in enumerate(evergreen_bi, 1):
            folder_name = f"{i:02d}-{phrase.replace(' ', '-').replace(chr(39), '')}"
            folder_path = os.path.join(trends_week_dir, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
                created_folders.append(folder_name)
                # 빈 README 생성 (GitHub 웹에서 폴더가 보이도록)
                readme_path = os.path.join(folder_path, "README.md")
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(f"# {phrase}\n\n"
                            f"Google Trends CSV를 이 폴더에 업로드하세요.\n\n"
                            f"- `time_series_*.csv` — 시계열 데이터\n"
                            f"- `searched_with_top-*.csv` — 연관검색어 상위\n"
                            f"- `searched_with_rising-*.csv` — 급상승 검색어\n")
        if created_folders:
            print(f"📁 Trends 폴더 {len(created_folders)}개 자동 생성: {trends_week_dir}")
    except Exception as e:
        print(f"⚠️ Trends 폴더 생성 실패 (무시): {e}")

    return "\n".join(lines)


# =====================================================================
# 메인
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("📊 주간 리서치 스캔 v4 (수동 분석 모드 — AI 호출 없음)")
    print("=" * 60 + "\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now      = datetime.now(timezone.utc)
    week_tag = now.strftime("%Y-W%W")

    # [1] 수집
    items = collect_news() + collect_community() + collect_reddit()
    if not items:
        print("⚠️ 수집된 항목이 없습니다.")
        raise SystemExit(1)
    print(f"\n✅ 총 {len(items)}건 수집 완료\n")

    # 주차별 폴더 생성 (research_data/weekly/YYYY-WW/)
    week_dir = os.path.join(WEEKLY_DIR, week_tag)
    os.makedirs(week_dir, exist_ok=True)

    # 원시 데이터 저장 (월간 분석에서 재사용)
    raw_path = os.path.join(week_dir, "raw_research_log.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump({
            "week_tag":     week_tag,
            "collected_at": now.isoformat(),
            "sources":      [s["source"] for s in NEWS_SOURCES + COMMUNITY_SOURCES],
            "item_count":   len(items),
            "items":        items,
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 원시 데이터: {raw_path}")

    # [2] 빈도
    top_uni, top_bi = build_frequency(items)

    # [3-A] AI용 프롬프트 파일 (Gemini 첨부용)
    prompt_filename = "prompt.txt"
    prompt_path     = os.path.join(week_dir, prompt_filename)
    prompt_text     = build_ai_prompt(top_uni, top_bi, items, week_tag)
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt_text)
    prompt_size_kb = len(prompt_text.encode("utf-8")) / 1024
    print(f"🤖 AI 프롬프트: {prompt_path} ({prompt_size_kb:.1f} KB)")

    # [3-B] 사람용 리포트
    report      = build_human_report(top_uni, top_bi, items, week_tag, prompt_path)
    report_path = os.path.join(week_dir, "manual_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"📄 사람용 리포트: {report_path}")

    print(f"\n🏁 완료! (비용 발생 없음)")
    print(f"\n다음 단계:")
    print(f"  1. {prompt_path} 파일을 Gemini에 첨부")
    print(f"  2. JSON 결과 받기 → 앱 기획 탭에 저장")
    print(f"  3. 기획안 선택 + parent_hub 귀속")
    print(f"  4. Trends/KP CSV 수집 → Grade 판정")
