# =====================================================================
# ✍️ 글 생성 파이프라인 (write.py) — v4
# =====================================================================
# 목적: content_pipeline.json의 기획안을 바탕으로
#       Gemini에 넘길 글쓰기 프롬프트 생성 + 팩트체크 프롬프트 생성
#
# 설계 철학 (v4에서 변경):
#   코드 = 수집 + 거친 필터 (프롬프트 크기 제한용)
#   Gemini = 관련성 최종 판단 + 글 생성
#   → 문자열 매칭으로 의미 판단을 하려던 시도를 폐기.
#     명백한 무관 소스(구문 0개 매칭)만 코드가 제거하고,
#     최종 관련성 판단은 Gemini가 SOURCE RELEVANCE RULE로 수행.
#
# 사용법:
#   python write.py list                    → 발행 대기 기획안 목록
#   python write.py prep [클러스터명]       → 글쓰기 프롬프트 생성
#     --mode jina   : 다단계 원문 수집 (기본값)
#     --mode title  : 제목만으로 강제 생성
#   python write.py review [클러스터명]     → 검증+수정 프롬프트 생성 (Claude용)
#   python write.py done [클러스터명]       → 발행 완료 기록
#   python write.py check-tiers            → 소스 등급 현황 확인
#
# 원문 수집 5단계 (각 단계에서 후보 2개 이상 모이면 다음 단계 스킵):
#   1단계: raw_research_log → open 소스
#   2단계: Wikipedia API
#   3단계: Reddit JSON API
#   4단계: DuckDuckGo 공홈 탐색
#   5단계: 제목 모드 전환
# =====================================================================

import os
import re
import sys
import json
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

import requests

# posts_manager는 선택적 import (없어도 동작)
try:
    from posts_manager import register_post
    _POSTS_MANAGER_OK = True
except ImportError:
    _POSTS_MANAGER_OK = False

# ── 경로 설정 ──
PIPELINE_FILE = "content_pipeline.json"
CONFIG_FILE   = "config.json"
OUTPUT_DIR    = "research_data"

# 글 생성 파이프라인 하위 폴더 (정리된 구조)
WRITE_DIR     = os.path.join(OUTPUT_DIR, "write")        # 글쓰기 파이프라인 루트
PROMPTS_DIR   = os.path.join(WRITE_DIR, "prompts")       # 자동 생성 프롬프트
DRAFTS_DIR    = os.path.join(WRITE_DIR, "drafts")        # Gemini 초안
FINAL_DIR     = os.path.join(WRITE_DIR, "final")         # Claude 검증+수정 최종본
PUBLISHED_DIR = os.path.join(WRITE_DIR, "published")     # 발행 아카이브 (Jekyll 규격 파일명)

JINA_BASE      = "https://r.jina.ai/"
JINA_MAX_CHARS = 3000

# 페이월 감지 — 명확한 표현만 (오탐 방지)
PAYWALL_MIN_CHARS = 500
PAYWALL_KEYWORDS  = [
    "subscribe to read", "subscribe to continue",
    "subscribe to access", "sign in to read",
    "members only", "create an account to read",
    "start your free trial", "unlock this article",
    "premium members", "paid subscribers",
]

# 거친 필터: 이 점수 미만이면 명백한 무관 → 코드가 제거
# (정밀 판단이 아님. Gemini가 최종 판단하므로 느슨하게 설정)
NOISE_FILTER_SCORE = 3

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# =====================================================================
# 설정 로드/저장
# =====================================================================

def load_config():
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_source_tier(source_name, cfg):
    tiers = cfg.get("source_tiers", {})
    name  = source_name.lower().replace("r/", "")
    if name in [s.lower() for s in tiers.get("paywall", [])]:
        return "paywall"
    if name in [s.lower() for s in tiers.get("title_only", [])]:
        return "title_only"
    return "open"


def register_paywall(source_name, cfg):
    tiers        = cfg.setdefault("source_tiers", {})
    paywall_list = tiers.setdefault("paywall", [])
    name         = source_name.lower()
    if name not in [s.lower() for s in paywall_list]:
        paywall_list.append(name)
        open_list = tiers.get("open", [])
        tiers["open"] = [s for s in open_list if s.lower() != name]
        save_config(cfg)
        return True
    return False


def is_paywall_content(text):
    if len(text) < PAYWALL_MIN_CHARS:
        return True, "본문 길이 부족"
    text_lower = text.lower()
    for kw in PAYWALL_KEYWORDS:
        if kw in text_lower:
            return True, f"구독 키워드 감지: '{kw}'"
    return False, ""


# =====================================================================
# 유틸
# =====================================================================

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def load_pipeline():
    try:
        with open(PIPELINE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ {PIPELINE_FILE} 없음. pipeline.py select 먼저 실행하세요.")
        sys.exit(1)


def save_pipeline(data):
    data["_last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(PIPELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_week_tag():
    return datetime.now(timezone.utc).strftime("%Y-W%W")


def find_cluster(data, cluster_name, content_type=None):
    """
    cluster_name + content_type으로 기획안 탐색.
    content_type 지정 시: 해당 TYPE이고 status != published인 것 우선.
    content_type 미지정 시: 기존 동작 유지 (첫 번째 매칭).
    """
    ct = (content_type or "").upper().strip()

    # 1차: weekly_selections에서 cluster_name + content_type 정확 매칭
    if ct:
        for week, sels in sorted(data.get("weekly_selections", {}).items(), reverse=True):
            for sel in sels:
                if (cluster_name.lower() in sel["cluster_name"].lower()
                        and sel.get("content_type", "").upper() == ct
                        and sel.get("status") != "published"):
                    return sel
        # published 포함해서 재시도 (content_type만 맞으면 반환)
        for week, sels in sorted(data.get("weekly_selections", {}).items(), reverse=True):
            for sel in sels:
                if (cluster_name.lower() in sel["cluster_name"].lower()
                        and sel.get("content_type", "").upper() == ct):
                    return sel

        # content_type을 명시했는데 못 찾으면 여기서 종료.
        # 이름만으로 폴백하면 엉뚱한 유형의 글을 쓰게 되므로 (자동화 시 치명적)
        # 아래 이름 기반 폴백으로 내려가지 않는다.
        return None

    # 2차: content_type 미지정 — 기존 동작 (첫 번째 매칭)
    for week, sels in sorted(data.get("weekly_selections", {}).items(), reverse=True):
        for sel in sels:
            if cluster_name.lower() in sel["cluster_name"].lower():
                return sel

    # 3차: covered_clusters fallback
    for name, info in data.get("covered_clusters", {}).items():
        if cluster_name.lower() in name.lower():
            info["cluster_name"] = name
            return info
    return None


def find_raw_log(week_tag=None):
    """
    raw_research_log 파일 찾기.
    버그 수정: week_tag가 주어지면 해당 주차 로그를 우선 탐색.
    (2주 전 기획안을 나중에 발행할 때 그 주의 URL을 정확히 찾기 위함)
    """
    if week_tag:
        specific = Path(OUTPUT_DIR) / f"raw_research_log_{week_tag}.json"
        if specific.exists():
            return specific
    logs = sorted(Path(OUTPUT_DIR).glob("raw_research_log_*.json"), reverse=True)
    return logs[0] if logs else None


def get_cluster_week(cluster_info):
    """기획안이 선택된 주차 추출. selected_at 또는 last_week 기반."""
    # weekly_selections에서 온 기획안: selected_at → 주차 변환
    selected_at = cluster_info.get("selected_at", "")
    if selected_at:
        try:
            dt = datetime.fromisoformat(selected_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-W%W")
        except (ValueError, AttributeError):
            pass
    # covered_clusters에서 온 기획안: last_week 사용
    return cluster_info.get("last_week", None)


def noise_score(text, hub_keyword, spoke_keywords):
    """
    거친 노이즈 필터용 점수. (정밀 관련성 판단 아님)
    목적: Obsidian Fallout처럼 완전 무관한 글만 걸러냄.
          최종 관련성 판단은 Gemini가 SOURCE RELEVANCE RULE로 수행.

    계산: 허브/스포크 키워드의 연속 2단어(bigram)가 본문에 등장하면 +1.
    """
    text_lower = text.lower()
    score      = 0
    phrases    = [hub_keyword] + list(spoke_keywords[:3])

    for phrase in phrases:
        words = [w for w in phrase.lower().split() if len(w) > 2]
        if len(words) >= 2:
            # 2단어 이상: bigram(연속 2단어) 매칭
            matched = False
            for i in range(len(words) - 1):
                bigram = words[i] + " " + words[i + 1]
                if bigram in text_lower:
                    score += 1
                    matched = True
                    break  # 구문당 1회만
        elif len(words) == 1:
            # 단일 단어 키워드: 단어 자체가 본문에 등장하면 +1
            # (단어 경계 매칭으로 부분일치 오탐 방지)
            if re.search(r'\b' + re.escape(words[0]) + r'\b', text_lower):
                score += 1
    return score


def fetch_jina(url, max_chars=JINA_MAX_CHARS):
    jina_url = f"{JINA_BASE}{url}"
    try:
        resp = requests.get(jina_url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            text = resp.text.strip()
            return text[:max_chars] if len(text) > max_chars else text
        return None
    except Exception as e:
        print(f"    ⚠️ Jina 실패: {e}")
        return None


# =====================================================================
# 1단계: raw_research_log 관련 원문
# =====================================================================

def find_urls_for_cluster(cluster_info):
    # 버그 수정: 기획안이 선택된 주차의 로그를 우선 탐색
    cluster_week = get_cluster_week(cluster_info)
    log_path     = find_raw_log(week_tag=cluster_week)
    if not log_path:
        return []

    # 어느 로그를 쓰는지 투명하게 표시 (주차 불일치 시 확인용)
    log_week = log_path.stem.replace("raw_research_log_", "")
    if cluster_week and log_week != cluster_week:
        print(f"  ℹ️  기획 주차({cluster_week}) 로그 없음 → 최신 로그({log_week}) 사용")

    with open(log_path, encoding="utf-8") as f:
        log = json.load(f)

    spoke_keywords = cluster_info.get("spoke_keywords", [])
    hub_keyword    = cluster_info.get("hub_keyword", "")

    matched = []
    for item in log.get("items", []):
        title = item.get("title", "").lower()
        link  = item.get("link", "")
        if not link:
            continue
        for kw in spoke_keywords + [hub_keyword]:
            kw_words = [w for w in kw.lower().split() if len(w) > 3]
            if kw_words and sum(1 for w in kw_words if w in title) >= min(2, len(kw_words)):
                matched.append({
                    "title":  item["title"],
                    "link":   link,
                    "source": item.get("source", ""),
                })
                break

    seen   = set()
    unique = []
    for m in matched:
        if m["link"] not in seen:
            seen.add(m["link"])
            unique.append(m)
    return unique[:6]


def collect_from_news(cluster_info, cfg):
    """1단계: raw_research_log open 소스에서 원문 수집."""
    urls           = find_urls_for_cluster(cluster_info)
    hub_keyword    = cluster_info.get("hub_keyword", "")
    spoke_keywords = cluster_info.get("spoke_keywords", [])
    sources        = []
    context_text   = ""
    ok_count       = 0

    for i, item in enumerate(urls, 1):
        source_name = item["source"].lower()
        tier        = get_source_tier(source_name, cfg)

        if tier in ("paywall", "title_only"):
            print(f"    [{i}/{len(urls)}] ⛔ {item['source']} [{tier.upper()}] 스킵")
            sources.append({"title": item["title"], "url": item["link"],
                            "source": item["source"], "tier": tier, "status": "skipped"})
            continue

        print(f"    [{i}/{len(urls)}] 🌐 {item['source']}: {item['title'][:45]}...")
        content = fetch_jina(item["link"])
        time.sleep(1)

        if not content:
            sources.append({"title": item["title"], "url": item["link"],
                            "source": item["source"], "status": "failed"})
            continue

        is_pw, reason = is_paywall_content(content)
        if is_pw:
            if register_paywall(source_name, cfg):
                print(f"    ⚠️  [{item['source']}] 페이월 감지 → paywall 자동 등록")
            sources.append({"title": item["title"], "url": item["link"],
                            "source": item["source"], "status": "paywall", "reason": reason})
            continue

        # 거친 노이즈 필터만 적용
        score = noise_score(content, hub_keyword, spoke_keywords)
        if score < NOISE_FILTER_SCORE:
            print(f"    🔸 노이즈 제거 (매칭 {score}) — 스킵")
            sources.append({"title": item["title"], "url": item["link"],
                            "source": item["source"], "status": "noise", "score": score})
            continue

        print(f"    ✅ 후보 수집 ({len(content)}자)")
        ok_count += 1
        sources.append({"title": item["title"], "url": item["link"],
                        "source": item["source"], "status": "ok", "chars": len(content)})
        context_text += f"\n\n--- SOURCE: {item['source']} ---\n"
        context_text += f"Title: {item['title']}\nURL: {item['link']}\n\n{content}"

    return ok_count, sources, context_text


# =====================================================================
# 2단계: Wikipedia API
# =====================================================================

def collect_from_wikipedia(hub_keyword, spoke_keywords):
    print(f"\n  📖 [2단계] Wikipedia 탐색: '{hub_keyword}'")

    search_url = "https://en.wikipedia.org/w/api.php"
    params     = {"action": "query", "list": "search",
                  "srsearch": hub_keyword, "srlimit": 3, "format": "json"}

    try:
        resp    = requests.get(search_url, params=params, headers=HEADERS, timeout=10)
        results = resp.json().get("query", {}).get("search", [])
    except Exception as e:
        print(f"    ⚠️ Wikipedia 검색 실패: {e}")
        return 0, [], ""

    if not results:
        print(f"    ⚠️ Wikipedia 결과 없음")
        return 0, [], ""

    sources, context_text, ok_count = [], "", 0

    for r in results[:2]:
        title    = r.get("title", "")
        page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        print(f"    🌐 Wikipedia: {title}")

        content = fetch_jina(page_url)
        time.sleep(1)
        if not content:
            continue

        score = noise_score(content, hub_keyword, spoke_keywords)
        if score < NOISE_FILTER_SCORE:
            print(f"    🔸 노이즈 제거 (매칭 {score}) — 스킵")
            continue

        print(f"    ✅ 후보 수집 ({len(content)}자)")
        ok_count += 1
        sources.append({"title": title, "url": page_url,
                        "source": "wikipedia", "status": "ok", "chars": len(content)})
        context_text += f"\n\n--- SOURCE: Wikipedia ({title}) ---\n"
        context_text += f"URL: {page_url}\n\n{content}"

    return ok_count, sources, context_text


# =====================================================================
# 3단계: Reddit JSON API
# =====================================================================

# =====================================================================
# 3단계: Reddit — Jina 기반 수집
# =====================================================================

# =====================================================================
# 3단계: 멀티 커뮤니티 수집
# (Hacker News / Steam 포럼 / Google Play / YouTube)
# =====================================================================

def _community_note(content, source_name):
    """커뮤니티 소스 공통 안내 문구."""
    return (f"\n(Note: {source_name} user content — "
            f"summarize reactions naturally, do NOT reproduce verbatim quotes in bulk)\n")


def collect_from_hackernews(hub_keyword, spoke_keywords):
    """Hacker News Algolia API — 인증 불필요, 범용."""
    print(f"\n    🔶 HN 탐색: '{hub_keyword}'")
    query    = quote_plus(hub_keyword)
    hn_url   = f"https://hn.algolia.com/api/v1/search?query={query}&tags=comment,story&hitsPerPage=10"
    try:
        resp = requests.get(hn_url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"      ⚠️ HN API 실패: HTTP {resp.status_code}")
            return 0, [], ""
        hits = resp.json().get("hits", [])
        if not hits:
            print(f"      ⚠️ HN 결과 없음")
            return 0, [], ""
    except Exception as e:
        print(f"      ⚠️ HN 요청 실패: {e}")
        return 0, [], ""

    sources, context_text, ok_count = [], "", 0
    for hit in hits[:5]:
        title    = hit.get("title") or hit.get("comment_text", "")[:80]
        story_id = hit.get("objectID", "")
        url      = f"https://news.ycombinator.com/item?id={story_id}"
        text     = (hit.get("story_text") or hit.get("comment_text") or "").strip()
        if not text:
            continue
        score = noise_score(title + " " + text, hub_keyword, spoke_keywords)
        if score < 1:
            continue
        print(f"      ✅ HN: {title[:50]} (매칭 {score})")
        ok_count += 1
        sources.append({"title": title, "url": url, "source": "hackernews", "status": "ok"})
        context_text += f"\n\n--- SOURCE: Hacker News ---\n"
        context_text += f"Title: {title}\nURL: {url}\n\n{text[:1500]}"
        context_text += _community_note(text, "Hacker News")
        if ok_count >= 3:
            break

    if ok_count == 0:
        print(f"      🔸 HN 관련 결과 없음")
    return ok_count, sources, context_text


def collect_from_steam_forums(hub_keyword, spoke_keywords):
    """Steam 커뮤니티 포럼 — 게임 관련 주제 전용, Jina 수집."""
    _gaming_keys = ["steam", "game", "gaming", "xbox", "playstation",
                    "nintendo", "assassin", "valve", "deck"]
    if not any(k in hub_keyword.lower() for k in _gaming_keys):
        return 0, [], ""

    print(f"\n    🎮 Steam 포럼 탐색: '{hub_keyword}'")
    query = quote_plus(hub_keyword)
    steam_urls = [
        f"https://steamcommunity.com/discussions/forum/0/?q={query}",
        f"https://www.google.com/search?q=site:steamcommunity.com+{query}",
    ]

    sources, context_text, ok_count = [], "", 0
    for url in steam_urls[:2]:
        if ok_count >= 2:
            break
        print(f"      🌐 Jina → Steam: {url[:70]}...")
        content = fetch_jina(url)
        time.sleep(1.5)
        if not content or len(content) < 200:
            continue
        score = noise_score(content, hub_keyword, spoke_keywords)
        if score < 1:
            print(f"      🔸 노이즈 제거 (매칭 {score})")
            continue
        print(f"      ✅ Steam 포럼 수집 ({len(content)}자)")
        ok_count += 1
        sources.append({"title": f"Steam Community: {hub_keyword}",
                        "url": url, "source": "steam_forum", "status": "ok"})
        context_text += f"\n\n--- SOURCE: Steam Community Forum ---\n"
        context_text += f"URL: {url}\n\n{content[:2000]}"
        context_text += _community_note(content, "Steam Community")

    if ok_count == 0:
        print(f"      🔸 Steam 포럼 관련 결과 없음")
    return ok_count, sources, context_text


def collect_from_google_play(hub_keyword, spoke_keywords):
    """Google Play 리뷰 — 앱 관련 주제 전용, Jina 수집."""
    _app_keys = ["health", "app", "android", "samsung", "google", "fitness",
                 "tracker", "monitor", "chrome", "browser", "extension"]
    if not any(k in hub_keyword.lower() for k in _app_keys):
        return 0, [], ""

    print(f"\n    📱 Google Play 리뷰 탐색: '{hub_keyword}'")
    # Jina로 Google Play 검색결과 수집
    query    = quote_plus(f"{hub_keyword} app review")
    jina_url = f"https://s.jina.ai/{query}+site:play.google.com"
    print(f"      🌐 Jina → Play: {jina_url[:70]}...")

    try:
        content = fetch_jina(jina_url)
        time.sleep(1.5)
    except Exception as e:
        print(f"      ⚠️ Google Play 수집 실패: {e}")
        return 0, [], ""

    if not content or len(content) < 200:
        print(f"      🔸 Google Play 내용 없음")
        return 0, [], ""

    score = noise_score(content, hub_keyword, spoke_keywords)
    if score < 1:
        print(f"      🔸 노이즈 제거 (매칭 {score})")
        return 0, [], ""

    print(f"      ✅ Google Play 수집 ({len(content)}자)")
    url = f"https://play.google.com/store/search?q={quote_plus(hub_keyword)}&c=apps"
    sources = [{"title": f"Google Play: {hub_keyword}",
                "url": url, "source": "google_play", "status": "ok"}]
    context_text  = f"\n\n--- SOURCE: Google Play Reviews ---\n"
    context_text += f"URL: {url}\n\n{content[:2000]}"
    context_text += _community_note(content, "Google Play")
    return 1, sources, context_text


def collect_from_youtube(hub_keyword, spoke_keywords, cfg):
    """YouTube Data API v3 — API 키 있을 때만 실행."""
    yt_api_key = cfg.get("youtube_api_key", "")
    if not yt_api_key:
        return 0, [], ""

    print(f"\n    🎬 YouTube 탐색: '{hub_keyword}'")
    # spoke_keywords 기반 구체적 쿼리 생성 (hub_keyword보다 구체적)
    yt_queries = []
    if spoke_keywords:
        yt_queries = [kw for kw in spoke_keywords[:3]]
    if hub_keyword not in yt_queries:
        yt_queries.append(hub_keyword)
    # 첫 번째 쿼리로 검색 시도, 결과 없으면 다음 쿼리
    items = []
    used_query = yt_queries[0]
    for yt_q in yt_queries:
        query = quote_plus(yt_q)
        print(f"      🔍 쿼리: '{yt_q}'")
        search_url = (f"https://www.googleapis.com/youtube/v3/search"
                      f"?part=snippet&q={query}&type=video&maxResults=5"
                      f"&relevanceLanguage=en&key={yt_api_key}")
        try:
            resp = requests.get(search_url, timeout=10)
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                if items:
                    used_query = yt_q
                    break
        except Exception:
            continue
    if not items:
        print(f"      ⚠️ YouTube 결과 없음")
        return 0, [], ""
    # 아래 try/except 블록을 건너뛰기 위한 dummy search_url
    search_url = ""

    sources, context_text, ok_count = [], "", 0
    for item in items[:3]:
        video_id = item["id"].get("videoId", "")
        title    = item["snippet"].get("title", "")
        if not video_id:
            continue
        # 댓글 수집
        comments_url = (f"https://www.googleapis.com/youtube/v3/commentThreads"
                        f"?part=snippet&videoId={video_id}&maxResults=10"
                        f"&order=relevance&key={yt_api_key}")
        try:
            cr = requests.get(comments_url, timeout=10)
            comments = []
            if cr.status_code == 200:
                for c in cr.json().get("items", []):
                    text = c["snippet"]["topLevelComment"]["snippet"].get("textDisplay", "")
                    if text:
                        comments.append(text[:300])
        except Exception:
            comments = []

        if not comments:
            continue

        combined = title + " " + " ".join(comments)
        score = noise_score(combined, hub_keyword, spoke_keywords)
        if score < 1:
            continue

        print(f"      ✅ YouTube: {title[:50]} ({len(comments)}개 댓글)")
        ok_count += 1
        yt_url = f"https://www.youtube.com/watch?v={video_id}"
        sources.append({"title": title, "url": yt_url,
                        "source": "youtube", "status": "ok"})
        context_text += f"\n\n--- SOURCE: YouTube Comments ({title[:50]}) ---\n"
        context_text += f"URL: {yt_url}\n\n"
        context_text += "\n".join(f"- {c}" for c in comments[:8])
        context_text += _community_note(combined, "YouTube")
        if ok_count >= 2:
            break

    if ok_count == 0:
        print(f"      🔸 YouTube 관련 결과 없음")
    return ok_count, sources, context_text


def collect_from_community(hub_keyword, spoke_keywords, cfg):
    """
    3단계 통합 커뮤니티 수집.
    Hacker News (범용) + Steam 포럼 (게임) + Google Play (앱) + YouTube (키 있을 때)
    → 커뮤니티 반응 섹션용 소스 최대 3개 수집
    """
    print(f"\n  👥 [3단계] 커뮤니티 수집: '{hub_keyword}'")
    all_sources, all_context, total_ok = [], "", 0

    # ① Hacker News (항상 시도)
    ok, sources, ctx = collect_from_hackernews(hub_keyword, spoke_keywords)
    all_sources += sources; all_context += ctx; total_ok += ok

    # ② Steam 포럼 (게임 키워드 감지 시)
    if total_ok < 3:
        ok, sources, ctx = collect_from_steam_forums(hub_keyword, spoke_keywords)
        all_sources += sources; all_context += ctx; total_ok += ok

    # ③ Google Play (앱 키워드 감지 시)
    if total_ok < 3:
        ok, sources, ctx = collect_from_google_play(hub_keyword, spoke_keywords)
        all_sources += sources; all_context += ctx; total_ok += ok

    # ④ YouTube (API 키 있을 때)
    if total_ok < 3:
        ok, sources, ctx = collect_from_youtube(hub_keyword, spoke_keywords, cfg)
        all_sources += sources; all_context += ctx; total_ok += ok

    if total_ok == 0:
        print(f"  ⚠️ 커뮤니티 수집 전체 실패 — 커뮤니티 섹션 생략됨")
    else:
        print(f"  → 3단계 결과: {total_ok}개 후보")

    return total_ok, all_sources, all_context


# =====================================================================
# 4단계: Jina 검색 기반 공홈/서포트 탐색
# =====================================================================

def collect_from_official(hub_keyword, spoke_keywords, cfg=None):
    if cfg is None:
        cfg = {}
    print(f"\n  🏠 [4단계] Jina 검색 기반 공홈 탐색: '{hub_keyword}'")

    OFFICIAL_DOMAINS = [
        "store.steampowered.com", "valvesoftware.com",
        "samsung.com", "store.google.com", "blog.google.com",
        "nvidia.com", "amd.com", "intel.com",
        "xbox.com", "playstation.com", "nintendo.com",
        "support.microsoft.com", "docs.microsoft.com",
        "developer.android.com", "support.google.com",
        "ubisoft.com", "epicgames.com",
        # Chrome / Chromium
        "developer.chrome.com", "chromium.org", "chrome.google.com",
        "blog.chromium.org", "chromewebstore.google.com",
        # Apple
        "developer.apple.com", "support.apple.com",
        # Mozilla / Firefox
        "developer.mozilla.org", "support.mozilla.org",
    ]

    # config.json의 cluster_domains에서 클러스터별 추가 도메인 로딩
    _cluster_domains = cfg.get("cluster_domains", {})
    direct_fetch_urls = []
    for _cluster_key, _cluster_cfg in _cluster_domains.items():
        if _cluster_key.startswith("_"):
            continue
        if _cluster_key.lower() not in hub_keyword.lower():
            continue
        # 구버전 호환 (리스트) + 신버전 (딕셔너리)
        if isinstance(_cluster_cfg, list):
            _domains = _cluster_cfg
            _direct = []
        else:
            _domains = _cluster_cfg.get("domains", [])
            _direct = _cluster_cfg.get("direct_urls", [])
        OFFICIAL_DOMAINS = list(set(OFFICIAL_DOMAINS + _domains))
        direct_fetch_urls += _direct
        print(f"    📌 cluster_domains 추가: {_domains}")
        if _direct:
            print(f"    📌 direct_urls 추가: {len(_direct)}개")

    # direct_urls 직접 fetch (Jina 검색 없이 바로 수집)
    sources, context_text, ok_count, seen_urls = [], "", 0, set()

    if direct_fetch_urls:
        print(f"    🎯 direct_urls 직접 fetch 시작 ({len(direct_fetch_urls)}개)")
        for d_url in direct_fetch_urls:
            if ok_count >= 3:
                break
            if d_url in seen_urls:
                continue
            seen_urls.add(d_url)
            print(f"    🌐 직접 fetch: {d_url[:70]}...")
            content = fetch_jina(d_url)
            time.sleep(1.5)
            if not content or len(content) < 200:
                print(f"    ⚠️ 내용 없음 — 스킵")
                continue
            is_pw, _ = is_paywall_content(content)
            if is_pw:
                print(f"    ⛔ 페이월 감지 — 스킵")
                continue
            score = noise_score(content, hub_keyword, spoke_keywords)
            if score < 1:
                print(f"    🔸 노이즈 제거 (매칭 {score}) — 스킵")
                continue
            print(f"    ✅ 직접 fetch 성공 ({len(content)}자)")
            ok_count += 1
            domain_name = next((d for d in OFFICIAL_DOMAINS if d in d_url), "official")
            sources.append({
                "title": f"{hub_keyword} ({domain_name})",
                "url": d_url,
                "source": "official_direct",
                "status": "ok",
                "chars": len(content),
            })
            context_text += f"\n\n--- SOURCE: Official Direct ({domain_name}) ---\n"
            context_text += f"URL: {d_url}\n\n{content[:3000]}"

    # Jina 검색 쿼리 목록 — 공홈/서포트 페이지 타겟
    search_queries = [
        f"{hub_keyword} official support",
        f"{hub_keyword} how to",
        f"site:samsung.com {hub_keyword}" if "samsung" in hub_keyword.lower() else f"{hub_keyword} guide",
    ]
    # spoke_keywords 기반 추가 쿼리
    for kw in spoke_keywords[:2]:
        search_queries.append(kw)

    for query in search_queries:
        if ok_count >= 3:
            break
        jina_search_url = f"https://s.jina.ai/{quote_plus(query)}"
        print(f"    🔍 Jina 검색: '{query}'")
        try:
            search_result = fetch_jina(jina_search_url)
            time.sleep(1.5)  # Jina 무료 플랜 속도 제한 대응
        except Exception as e:
            print(f"    ⚠️ Jina 검색 실패: {e}")
            continue
        if not search_result:
            continue

        # 검색 결과에서 공식 도메인 URL 추출 (Jina 자체 URL 제외)
        found_urls = re.findall(r'https?://[^\s\)\"\'<>\]]+', search_result)
        official_hits = []
        for url in found_urls:
            # Jina 자체 URL 제외 (s.jina.ai, r.jina.ai)
            if "jina.ai" in url:
                continue
            # 공식 도메인 매칭
            if any(domain in url for domain in OFFICIAL_DOMAINS):
                # URL 끝 불필요한 문자 제거
                url = url.rstrip(".,;)")
                if url not in seen_urls and url not in official_hits:
                    official_hits.append(url)

        if not official_hits:
            print(f"    🔸 공식 도메인 URL 없음 — 스킵")
            continue

        print(f"    🔍 공식 URL {len(official_hits)}개 발견")

        # 발견된 공식 URL을 Jina로 직접 fetch
        for url in official_hits[:2]:
            if ok_count >= 3:
                break
            if url in seen_urls:
                continue
            seen_urls.add(url)
            print(f"    🌐 공홈 수집: {url[:70]}...")
            content = fetch_jina(url)
            time.sleep(1.5)
            if not content:
                continue
            is_pw, _ = is_paywall_content(content)
            if is_pw:
                print(f"    ⛔ 페이월 감지 — 스킵")
                continue
            score = noise_score(content, hub_keyword, spoke_keywords)
            if score < NOISE_FILTER_SCORE:
                print(f"    🔸 노이즈 제거 (매칭 {score}) — 스킵")
                continue
            print(f"    ✅ 공홈 후보 수집 ({len(content)}자)")
            ok_count += 1
            domain_name = next((d for d in OFFICIAL_DOMAINS if d in url), "official")
            sources.append({
                "title":  f"{hub_keyword} ({domain_name})",
                "url":    url,
                "source": "official",
                "status": "ok",
                "chars":  len(content),
            })
            context_text += f"\n\n--- SOURCE: Official ({domain_name}) ---\n"
            context_text += f"URL: {url}\n\n{content[:3000]}"

    if ok_count == 0:
        print(f"    ⚠️ 공홈 Jina 수집 실패 — 소스 없음")

    return ok_count, sources, context_text


# =====================================================================
# 다단계 수집 통합
# =====================================================================

def collect_context_multistage(cluster_info, cfg):
    """
    4단계 전체 수집 — 스킵 없이 항상 전부 실행.
    풍부한 컨텍스트를 Gemini에 넘기는 것이 목표.
    최종 관련성 판단은 Gemini(SOURCE RELEVANCE RULE)가 수행.
    """
    hub_keyword    = cluster_info.get("hub_keyword", "")
    spoke_keywords = cluster_info.get("spoke_keywords", [])

    all_sources, all_context, total_ok = [], "", 0

    # ── 1단계: 뉴스 소스 ──
    print(f"\n  📰 [1단계] 뉴스 소스 탐색...")
    ok, sources, ctx = collect_from_news(cluster_info, cfg)
    all_sources += sources
    all_context += ctx
    total_ok    += ok
    print(f"  → 1단계 결과: {ok}개 후보")

    # ── 2단계: Wikipedia ──
    ok, sources, ctx = collect_from_wikipedia(hub_keyword, spoke_keywords)
    all_sources += sources
    all_context += ctx
    total_ok    += ok
    print(f"  → 2단계 결과: {ok}개 후보")

    # ── 3단계: 커뮤니티 (HN / Steam / Google Play / YouTube) ──
    ok, sources, ctx = collect_from_community(hub_keyword, spoke_keywords, cfg)
    all_sources += sources
    all_context += ctx
    total_ok    += ok

    # ── 4단계: 공홈 ──
    ok, sources, ctx = collect_from_official(hub_keyword, spoke_keywords, cfg)
    all_sources += sources
    all_context += ctx
    total_ok    += ok
    print(f"  → 4단계 결과: {ok}개 후보")

    print(f"\n  📦 전체 수집 완료: 총 {total_ok}개 후보")

    if total_ok >= 1:
        return {"mode": "jina", "sources": all_sources,
                "context_text": all_context.strip(), "total_ok": total_ok}

    # 전부 실패 → 제목 모드
    print(f"  ⚠️ 모든 단계 원문 수집 실패 → 제목 모드 전환")
    return collect_context_title(cluster_info)


def collect_context_title(cluster_info):
    """[제목 모드] 원문 없이 키워드 + 헤드라인만."""
    print("\n  📝 [제목 모드] 키워드 기반 컨텍스트 구성...")
    spoke_keywords = cluster_info.get("spoke_keywords", [])
    hub_keyword    = cluster_info.get("hub_keyword", "")
    urls           = find_urls_for_cluster(cluster_info)

    sources = [{"title": u["title"], "url": u["link"],
                "source": u["source"], "status": "title_only"} for u in urls]

    lines = [f"Hub keyword: {hub_keyword}", "",
             "Related headlines (use ONLY facts explicitly stated in these headlines):"]
    for kw in spoke_keywords:
        lines.append(f"  - {kw}")
    if urls:
        lines.append("")
        lines.append("Source headlines and URLs (for citation only):")
        for u in urls:
            lines.append(f"  - [{u['source']}] {u['title']}")
            lines.append(f"    {u['link']}")

    return {"mode": "title", "sources": sources,
            "context_text": "\n".join(lines), "total_ok": 0}


# =====================================================================
# 프롬프트 생성
# =====================================================================

def build_write_prompt(cluster_info, context_result):
    mode            = context_result["mode"]
    context_text    = context_result["context_text"]
    cluster_name    = cluster_info.get("cluster_name", "")
    content_type    = cluster_info.get("content_type", "GUIDE")
    suggested_title = cluster_info.get("suggested_title", "")
    hub_keyword     = cluster_info.get("hub_keyword", "")
    spoke_keywords  = cluster_info.get("spoke_keywords", [])
    competition     = cluster_info.get("competition_level", "MEDIUM")
    affiliate       = cluster_info.get("affiliate_potential", "LOW")
    timing          = cluster_info.get("timing", "NOW")
    trends_pattern  = cluster_info.get("trends_pattern", "UNKNOWN")
    total_ok        = context_result.get("total_ok", 0)

    # ── HUB 전용 프롬프트 ──────────────────────────────────────────
    if content_type == "HUB":
        spoke_articles = cluster_info.get("spoke_articles", [])

        # 스포크 소스 블록 생성
        spoke_block = ""
        for i, sp in enumerate(spoke_articles, 1):
            md_preview = sp.get('md_content', '')[:3000]
            ellipsis   = "..." if len(sp.get('md_content','')) > 3000 else ""
            spoke_block += (
                f"\n[SPOKE {i}]\n"
                f"Title:        {sp.get('title', '')}\n"
                f"URL:          {sp.get('url', '')}\n"
                f"Content Type: {sp.get('content_type', '')}\n"
                f"Full text:\n{md_preview}{ellipsis}\n"
            )

        # 스포크별 링크 예시 (지시문용)
        spoke_link_examples = ""
        for sp in spoke_articles:
            t = sp.get('title','')
            u = sp.get('url','')
            spoke_link_examples += f'     → Read more: [{t}]({u})\n'

        hub_prompt = (
            f'You are a writer for Frontbuffer Editorial, an independent tech/gaming media brand.\n'
            f'Write a HUB article that serves as the central entry point for the "{cluster_name}" cluster.\n\n'
            f'{"━"*39}\n'
            f'HUB ARTICLE BRIEF\n'
            f'{"━"*39}\n'
            f'Cluster:     {cluster_name}\n'
            f'Hub Keyword: {hub_keyword}\n'
            f'Hub Title:   {suggested_title}\n\n'
            f'{"━"*39}\n'
            f'SPOKE ARTICLES (your PRIMARY SOURCE)\n'
            f'{"━"*39}\n'
            f'{spoke_block}\n'
            f'{"━"*39}\n'
            f'HUB WRITING RULES (CRITICAL)\n'
            f'{"━"*39}\n'
            f'1. ROLE: This is a HUB — a navigation article that orients\n'
            f'   the reader and guides them to the right spoke.\n'
            f'   Do NOT try to cover everything. Your job is to connect.\n\n'
            f'2. VOICE: Analytical 3rd-person or editorial "we".\n'
            f'   NEVER use 1st-person ("I", "my", "me").\n'
            f'   NO fake personal experiences or anecdotes.\n\n'
            f'3. STRUCTURE:\n'
            f'   - H1: Use "{suggested_title}" EXACTLY as written\n'
            f'   - Intro (2-3 sentences): What this cluster covers + why it matters\n'
            f'     to someone who just searched "{hub_keyword}"\n'
            f'   - H2 per spoke: One section per spoke article\n'
            f'     * Start with: "If you are [reader type who needs this spoke]..."\n'
            f'     * Summarize the spoke in 3-5 sentences (NO verbatim copying)\n'
            f'     * End each section with the actual spoke link:\n'
            f'{spoke_link_examples}'
            f'   - Conclusion (2-3 sentences): Key takeaway tying all spokes together\n\n'
            f'4. NO DUPLICATION: Summarize each spoke in your own words.\n'
            f'   Do NOT copy spoke content verbatim. 3-5 sentences per spoke max.\n\n'
            f'5. INTERNAL LINKS: Every spoke MUST be linked with\n'
            f'   descriptive anchor text matching the spoke title exactly.\n'
            f'   Use the exact URLs provided in the SPOKE ARTICLES section above.\n\n'
            f'6. READER SORTING: Each H2 must clearly tell the reader\n'
            f'   whether THIS spoke is right for THEM.\n'
            f'   Example: "If you are not sure why your extension stopped working..."\n\n'
            f'7. WORD COUNT: 600-900 words.\n'
            f'   Hub is a navigator, not a deep dive — keep it concise.\n\n'
            f'8. SOURCES FOOTER:\n'
            f'   List only the spoke article links used.\n'
            f'   Format: - [Spoke Title](URL)\n\n'
            f'OUTPUT: Full article in English markdown.\n'
            f'No preamble. Start directly with the article.\n'
        )
        return hub_prompt

    # ── 기존 스포크 프롬프트 (HUB 아닌 모든 타입) ───────────────────

    # LISTICLE/COMPARISON인데 소스에 구체적 개체(제품/서비스명)가 부족한 경우 사전 경고
    concrete_entity_warning = ""
    if content_type in ("LISTICLE", "COMPARISON") and mode != "title":
        # 소스 텍스트에서 고유명사 패턴(대문자 시작 2단어 이상 조합) 대략 카운트
        _proper_nouns = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+){1,2}\b', context_text)
        _unique_nouns = set(_proper_nouns)
        if len(_unique_nouns) < 5:
            concrete_entity_warning = f"""
⚠️ SOURCE COVERAGE WARNING ({content_type}):
The collected sources appear to lack specific named products/services/tools
required for a {content_type.lower()}. Before writing:
- Use widely-known, generally accepted facts to fill in concrete examples
  (e.g. actual product names, real alternatives, or real comparison points).
- Mark any specific claim you cannot verify from sources or general knowledge
  as [NEEDS VERIFICATION] rather than inventing details.
- A {content_type.lower()} MUST include at least 3 concrete, named items —
  do not settle for abstract/conceptual points only.
"""

    if mode == "title":
        mode_block = """
⚠️ TITLE-ONLY MODE: No full article text is available.
- Do NOT invent specific numbers, specs, prices, or dates
- Use only facts explicitly stated in the headlines
- For any specific claim not in headlines: write [NEEDS VERIFICATION]
- You MAY use general, widely-known technical knowledge to add depth
- Target 800-1000 words despite limited source material
"""
        relevance_block = ""
    else:
        mode_block = f"""
✅ FULL-TEXT MODE: {total_ok} candidate source(s) provided below.
- Base ALL specific claims strictly on the source text
- Do NOT add information not present in the sources
- Cite sources using [Source: URL] format after each specific claim
"""
        # 핵심: Gemini가 관련성 판단
        relevance_block = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SOURCE RELEVANCE RULE (READ FIRST — CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The sources below were auto-collected and MAY include irrelevant articles.

STEP 1 — Evaluate each source:
  Is it actually about "{cluster_name}" (hub: "{hub_keyword}")?
  A source that merely mentions the product but discusses a DIFFERENT topic
  (e.g. a WiFi update, an unrelated game running on the device) is NOT relevant.

STEP 2 — Use ONLY relevant sources. Completely ignore irrelevant ones.
  Do NOT force irrelevant content into the article.

STEP 3 — At the VERY TOP of your output, before the article, report:
  [SOURCES USED: list source names you actually used]
  [DISCARDED: source name — one-line reason, for each ignored source]

STEP 4 — If NO source is actually relevant:
  Write "[⚠️ NO RELEVANT SOURCES]" at the top, then write the article
  using only the headlines/keywords and mark specifics as [NEEDS VERIFICATION].
"""

    spoke_str = "\n".join(f"  - {kw}" for kw in spoke_keywords)

    # 검증된 키워드 블록 (Trends+KP 분석 후 존재)
    verified_keywords = cluster_info.get("verified_keywords", [])
    data_grade        = cluster_info.get("data_grade", "")

    if verified_keywords:
        # LOW/MEDIUM 경쟁 + 월 100 이상
        strong_vk = [v for v in verified_keywords
                     if v.get("monthly_searches", 0) >= 100
                     and v.get("competition", "HIGH") in ("LOW", "MEDIUM", "?")]

        if strong_vk:
            # 롱테일(3단어+) 우선으로 spoke_str 교체
            longtail_vk = [v for v in strong_vk if len(v["keyword"].split()) >= 3]
            short_vk    = [v for v in strong_vk if len(v["keyword"].split()) < 3]

            # 롱테일 2개 + 짧은 것 1개 조합 (없으면 있는 것으로 채움)
            top_spoke = (longtail_vk[:2] + short_vk[:1])[:3]
            if not top_spoke:
                top_spoke = strong_vk[:3]

            spoke_str = "\n".join(f"  - {v['keyword']}" for v in top_spoke)

        # 표시용: 롱테일 우선 정렬해서 6개
        display_vk = strong_vk[:6] if strong_vk else verified_keywords[:6]
        longtail_count = sum(1 for v in display_vk if len(v["keyword"].split()) >= 3)

        vk_lines = "\n".join(
            f"  - \"{v['keyword']}\" "
            f"({'LONGTAIL ' if len(v['keyword'].split()) >= 3 else ''}월 {v['monthly_searches']:,}, "
            f"경쟁: {v.get('competition','?')})"
            for v in display_vk)

        verified_block = f"""
VERIFIED SEARCH TERMS (KP-validated from hub keyword, grade: {data_grade or 'B'}):
  ※ 롱테일({longtail_count}개)이 Target Keywords에 자동 반영됐습니다.
{vk_lines}
  → 위 Target Keywords는 실제 검색량 기반 롱테일로 교체됐습니다.
  → 롱테일 키워드는 본문 문장 안에 자연스럽게 녹여 쓰세요 (검색 의도 반영 목적).
  → H2 제목에 억지로 끼워넣지 마세요. 한 제목에 서로 다른 롱테일을 두 개 이상
    넣으면 부자연스러운 제목이 됩니다 (예: "X: Deploying Y and Z Solutions" 형태 금지).
    제목은 읽는 사람이 이해하기 쉬운 자연스러운 한국어/영어 문장이어야 합니다.
  → LOW 경쟁 롱테일을 우선 사용하면 신규 블로그도 1페이지 진입 가능성이 높아집니다.
"""
    elif data_grade == "B":
        verified_block = "\n(Note: 타이밍 검증됨 — KP 검색량 미검증, 롱테일은 Gemini 추측)\n"
    else:
        verified_block = ""

    prompt = f"""You are a writer for LIFO-LIKE Editorial, an independent tech/gaming media brand.
Write a high-quality, evergreen blog post based on the information provided.
{mode_block}{relevance_block}{concrete_entity_warning}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARTICLE BRIEF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cluster:         {cluster_name}
Content Type:    {content_type}
Suggested Title: {suggested_title}
Hub Keyword:     {hub_keyword}
Target Keywords:
{spoke_str}
Competition:     {competition}
Affiliate:       {affiliate}
Timing:          {timing}
Trends Pattern:  {trends_pattern}
{verified_block}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WRITING RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STYLE AND TONALITY (CRITICAL — READ FIRST)
1. VOICE: Write in analytical 3rd-person or editorial "we".
   NEVER use 1st-person singular ("I", "my", "me", "I've seen", "In my experience").

2. NO FAKE EXPERIENCES: Do NOT fabricate personal anecdotes, hands-on tests,
   or fake troubleshooting stories. Maintain an authoritative,
   research-backed journalistic tone throughout.

3. NATURAL FLOW: Avoid mechanical, documentation-style phrasing.
   Replace passive constructions with active, engaging 3rd-person phrasing.
   ❌ "proper preparation of physical media is necessary"
   ✅ "Before diving into the installation, preparing the right media ensures a smooth setup"
   ❌ "It should be noted that..."
   ✅ "Worth keeping in mind: ..."

4. CITATION EMBEDDING: NEVER output raw source tags like "[Source: URL]" at the
   end of sentences. Instead, naturally embed hyperlinks into relevant anchor text.
   ❌ "Valve released the drivers [Source: https://help.steampowered.com/...]"
   ✅ "According to [Valve's official Windows Resources](https://help.steampowered.com/...), the drivers..."
   ✅ "[Valve's driver page](URL) lists five packages required for full hardware support."

# STRUCTURE
5. STRUCTURE:
   - H1: MUST use the Suggested Title above EXACTLY as written.
     Do NOT change, rephrase, or substitute it.
     ✓ Using: "{suggested_title}" verbatim
   - Introduction: 2-3 sentences, hook + what reader will learn
   - H2 sections: 3-5 sections — vary length naturally by importance
     (avoid perfectly uniform section sizes — it reads as machine-generated)
   - Conclusion: Key takeaway + [INTERNAL LINK: related topic]
   - Word count: 800-1200 words

6. SEO:
   - Hub keyword in H1 and first paragraph
   - Long-tail keywords belong in body sentences, not forced into H2 headings.
     NEVER combine two different long-tail keywords into one H2 title
     (e.g. "X: Deploying Y and Z Solutions" is a red flag — reads as keyword-stuffed).
     H2 titles must read naturally, as a human editor would write them.

7. AFFILIATE (potential: {affiliate}):
   - HIGH/MEDIUM: include 1-2 [AFFILIATE LINK: product name] placeholders
   - LOW: skip affiliate mentions

8. INFORMATION BOUNDARY:
   - Covers ONLY: {cluster_name}
   - Other topics: mention briefly + [INTERNAL LINK: topic] only

9. COMMUNITY REACTION SECTION (REQUIRED if community sources are available):
   - Community sources include: YouTube comments, Hacker News, Steam forums,
     Google Play reviews, or other forum/user-discussion sources in the material.
   - Add ONE section near the end of the article covering real user reactions
     drawn from those community sources.
   - DO NOT use a generic title like "What Users Are Saying".
     Instead, write a section title that fits the article's tone and topic naturally.
     Examples (choose or invent something fitting):
       ✅ "Early Adopter Reports" / "In Practice: Owner Experiences"
       ✅ "Community Findings" / "What Owners Have Discovered"
       ✅ "From the Field" / "The Community Verdict"
   - Summarize 2-3 distinct user experiences or findings.
     Quote briefly and naturally — do NOT list bullet points of raw quotes.
   - If NO community sources are available in the source material,
     SKIP this section entirely. Do NOT fabricate community reactions.

10. SOURCES FOOTER:
   ---
   Sources: [list only the anchor-text hyperlinks used in the article, one per line]
   
   Note: Do NOT include "AI-assisted" or any AI disclosure in the article body.
   AI usage disclosure is handled separately on the site's Disclosure page.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SOURCE MATERIAL (candidates — evaluate relevance per rule above)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{context_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Follow the SOURCE RELEVANCE RULE first (report used/discarded),
then write the complete article in English.
No preamble beyond the required source report."""

    return prompt


def build_review_prompt(cluster_info, draft_text):
    """
    Claude 대화창에 붙여넣는 통합 검증+수정 프롬프트.
    한 번의 대화로: 위험 주장 추출 → 웹검색 검증 → 수정 반영 최종본 출력.
    (기존 factcheck + verify + 최종수정 3단계를 1단계로 통합)
    HUB content_type은 별도 분기로 처리 (팩트체크 대신 구조/링크 검증)
    """
    cluster_name = cluster_info.get("cluster_name", "")
    hub_keyword  = cluster_info.get("hub_keyword", "")
    content_type = cluster_info.get("content_type", "GUIDE")
    urls         = find_urls_for_cluster(cluster_info)
    url_list     = "\n".join(f"  - {u['link']}" for u in urls) if urls else "  (없음)"

    # 동일 클러스터 기존 발행글 URL 목록 (정합성 체크용)
    try:
        _pipe = load_pipeline()
        _published_in_cluster = [
            f"  - [{p.get('content_type','')}] {p.get('url','')}"
            for p in _pipe.get("published", [])
            if p.get("cluster_name") == cluster_name
        ]
        published_urls_block = (
            "\n".join(_published_in_cluster)
            if _published_in_cluster else "  (이 클러스터 기존 발행글 없음)"
        )
    except Exception:
        published_urls_block = "  (조회 실패)"

    # ── HUB 전용 리뷰 프롬프트 ──────────────────────────────────────
    if content_type == "HUB":
        # 스포크 URL 목록 추출 (build_write_prompt에서 주입된 spoke_articles 활용)
        spoke_articles = cluster_info.get("spoke_articles", [])
        spoke_url_block = "\n".join(
            f"  - [{sp.get('content_type','')}] {sp.get('url','')}"
            for sp in spoke_articles
        ) if spoke_articles else published_urls_block

        return f"""아래는 Frontbuffer Editorial 블로그에 발행할 HUB 영문 초안입니다.
HUB 글은 팩트 검증보다 구조·링크·독자 경험을 검증하는 것이 핵심입니다.
다음 순서대로 검토하고 최종본을 출력해주세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
작업 순서
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1단계] 내부 링크 검증
  아래 스포크 URL이 초안에 모두 포함되어 있는지 확인하세요.
  누락된 링크는 해당 섹션 말미에 추가하세요.

  스포크 URL 목록:
{spoke_url_block}

  체크 항목:
  - 각 스포크 URL이 초안에 정확히 존재하는가 (오타·경로 오류 포함)
  - 앵커 텍스트가 스포크 제목과 정확히 일치하는가
  - "→ Read more:" 또는 동등한 CTA 형식이 각 스포크 섹션 말미에 있는가

[2단계] 구조 검증
  체크 항목:
  - H1 제목이 기획안 제목과 정확히 일치하는가
  - 스포크 수만큼 H2 섹션이 존재하는가
  - 각 H2 섹션이 "If you are..." 또는 동등한 독자 분류 문장으로 시작하는가
  - 도입부(Intro)가 2~3문장인가
  - 결론(Conclusion)이 2~3문장인가
  - Sources 섹션에 스포크 링크가 모두 포함되어 있는가

[3단계] 독자 경험 검증
  체크 항목:
  - 도입부가 비기술 독자도 이해할 수 있는 언어로 작성됐는가
    (과도한 전문 용어나 긴 복합 문장이 없는가)
  - 각 H2의 독자 분류 문장이 구체적인 상황을 묘사하는가
    (예: "If you are a user who wants to..." 수준이 아니라
         "If you opened Chrome one day and your extension stopped working..." 수준)
  - 결론이 boilerplate(어디에나 붙일 수 있는 일반 문장)가 아닌가
    boilerplate 판단 기준: 클러스터명을 지워도 의미가 통하면 boilerplate

[4단계] 단어 수 체크
  - 초안 단어 수를 카운트하세요.
  - 600단어 미만: 에러 — 어느 섹션을 보강해야 하는지 구체적으로 제시
  - 600~900단어: 정상
  - 900단어 초과: 경고 — 어느 섹션을 축약해야 하는지 구체적으로 제시
    (HUB는 내비게이터 역할이므로 900단어 초과 시 스포크 역할 침범 가능성)

[5단계] 판정 리포트 (한국어)
  위 1~4단계 결과를 항목별로 정리하세요.
  형식:
    [내부링크] ✅/❌/⚠️ — 설명
    [구조]     ✅/❌/⚠️ — 설명
    [독자경험] ✅/❌/⚠️ — 설명
    [단어수]   N단어 — ✅/❌/⚠️

[6단계] 수정 반영된 최종본 출력
  5단계 판정에서 ❌/⚠️ 항목을 반영해서 수정된 완성본을 출력하세요.
  - 누락 링크 추가
  - boilerplate 결론 → 클러스터 특화 문장으로 교체
  - 독자 분류 문장이 generic하면 구체적 상황 묘사로 교체
  - 도입부 문장이 과도하게 복잡하면 간결하게 재작성
  - 단어 수 범위(600~900) 초과/미달 시 보강 또는 축약
  - 최종본은 ```markdown 코드블록``` 안에 출력

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
참고 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
클러스터: {cluster_name}
허브 키워드: {hub_keyword}
Content Type: HUB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
초안
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{draft_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
위 6단계를 순서대로 수행해주세요.
판정 리포트는 한국어로, 최종본은 영문 markdown 코드블록으로 출력하세요."""

    # ── 기존 스포크 리뷰 프롬프트 ───────────────────────────────────
    prompt = f"""아래는 LIFO-LIKE Editorial 블로그에 발행할 영문 초안입니다.
당신은 이 초안의 팩트를 검증하고 수정하는 편집자입니다.
웹 검색을 사용해서 다음 작업을 한 번에 수행해주세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
작업 순서
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1단계] 위험 주장 추출
  초안에서 다음에 해당하는 주장을 모두 찾으세요:
    - 구체적 수치/스펙/가격/날짜
    - 인물/조직의 인용
    - 비교 주장 ("X가 Y보다 빠르다")
    - [NEEDS VERIFICATION] 으로 표시된 부분

[1.5단계] 소스 보강 및 정합성 체크 (전체 content_type 적용)
  아래 체크리스트는 content_type에 관계없이 항상 수행하세요.
  보강으로 추가한 내용은 판정 리포트에 별도 표시:
    [보강 N] "추가한 내용 요약" — 출처 URL

  ⚠️ 공통 필수 체크 (모든 content_type):
  - **URL 실존 확인:** 초안의 모든 외부 링크(YouTube, 공식 문서, GitHub 등)를
    웹 검색으로 실제 존재하는지 확인하세요.
    존재하지 않는 URL은 즉시 제거하거나 올바른 URL로 교체하세요.
  - **제목-내용 정합성:** 제목이 독자에게 약속하는 내용이 본문에 실제로 있는지 확인하세요.
    없으면 웹 검색으로 찾아서 최종본에 반드시 보강하세요.
    예: 제목이 "Best X alternatives"인데 실제 대안 목록이 없으면 → 웹검색으로 찾아 추가
  - **현재 상태 확인:** 초안에서 "기능이 없다", "지원하지 않는다"고 주장하는 경우
    현재도 유효한지 웹 검색으로 확인하세요.
    최근 업데이트로 기능이 추가됐을 수 있어요.
  - **[NEEDS VERIFICATION] 처리:** 반드시 공식 소스로 채우세요.
    공식 소스로 확인 불가한 경우에만 해당 문장을 삭제하거나 일반화하세요.

  ⚠️ content_type별 추가 체크:

  GUIDE:
  - 단계별 절차가 공식 문서와 일치하는지 확인하세요.
    공식 지원 페이지(예: samsung.com/support 등)를 직접 웹 검색해서
    정확한 절차를 확인하고 누락된 핵심 단계나 주의사항을 추가하세요.
  - 앱 UI 메뉴 경로가 현재 버전과 일치하는지 확인하세요.

  LISTICLE:
  - 제목이 약속한 목록(대안, 추천, 순위 등)이 본문에 실제로 존재하는지 확인하세요.
  - 목록 항목이 부족하거나 구체성이 없으면 웹 검색으로 실제 사례/제품/도구를
    찾아서 보강하세요. 최소 3개 이상의 구체적 항목이 있어야 해요.
  - 각 항목의 현재 존재 여부 및 정확성을 확인하세요.
    (예: 앱/서비스가 현재도 운영 중인지, 가격/스펙이 맞는지)

  COMPARISON:
  - 비교 대상 양쪽 정보가 균형있게 다뤄지는지 확인하세요.
  - 한쪽 소스만 있고 다른 쪽이 부족하면 웹 검색으로 보강하세요.
  - 비교 기준(가격, 성능, 기능 등)이 공정하게 적용됐는지 확인하세요.

  EXPLAINER:
  - 핵심 개념 정의가 공식 소스와 일치하는지 확인하세요.
  - 설명이 현재 시점에도 정확한지 확인하세요.
    (기술/정책은 빠르게 변할 수 있어요)

[2단계] 웹 검색으로 검증
  각 주장을 웹 검색으로 확인하고 판정하세요:
    ✅ 사실       — 근거 URL 제시
    ❌ 틀림       — 올바른 내용 + 근거 URL
    ⚠️ 부분 수정  — 어떻게 고쳐야 하는지 + 근거 URL

  ⚠️ 교차확인 원칙:
    - 신제품/최신 이슈 관련 수치·스펙은 단일 소스로 판정하지 마세요.
      같은 주장을 다루는 독립 출처 2개 이상을 확인한 뒤 판정하세요.
    - 여러 매체가 동일 소스를 베낀 경우(초기 보도 인용 반복)는
      원본 소스(공식 문서, 제조사 발표)를 직접 찾아 확인하세요.

[3단계] 판정 리포트 (한국어)
  각 주장별로 판정 결과를 한국어로 간단히 정리하세요.
  형식:
    [검증 N] "주장 요약"
    판정: ✅/❌/⚠️
    근거: (한국어 설명 + URL)

[4단계] 클러스터 내 기존 발행글 정합성 체크
  아래 기존 발행글과 이 초안 사이에 사실 충돌이 있는지 확인하세요.
  특히 스펙(수치, 슬롯 수, 용량 등)이 서로 다르게 기술된 부분을 찾으세요.

  기존 발행글 (동일 클러스터):
{published_urls_block}

  충돌 발견 시:
    [충돌 N] "충돌 내용 요약"
    기존 글: (기존 발행글의 내용)
    이 초안: (이 초안의 내용)
    정확한 내용: (웹 검색으로 확인한 정답 + 근거 URL)

  충돌 없으면: "기존 발행글과 충돌 없음" 한 줄로 표기

[5단계] 수정 반영된 최종본 출력
  2단계·4단계 판정 결과를 반영해서 초안을 수정한 완성본을 출력하세요.
    - ❌/⚠️ 항목은 정확한 내용으로 교체
    - 클러스터 내 충돌은 정확한 수치로 통일
    - [NEEDS VERIFICATION] 표시는 검증 후 모두 제거
      (검증 불가한 것만 문장을 삭제하거나 일반화)
    - [Source: URL] 인용을 실제 검증한 URL로 채우기
    - 문체는 분석적 편집부 톤(we/third-person) 유지

  ⚠️ 분량 체크 (자동화 품질 기준):
    - 최종본이 800단어 미만이면 관련 내용을 보강해서 800단어 이상으로 맞추세요.
    - 보강 방법: 검증 과정에서 찾은 공식 문서 내용 중 독자에게 유용한 정보를
      새 섹션 또는 기존 섹션 확장으로 자연스럽게 추가하세요.
    - 억지로 늘리지 말고 실제로 유용한 내용만 추가하세요.
      (예: 대안적 백업 방법, 주의사항 추가, 관련 기능 설명 등)
    - 최종본은 ```markdown 코드블록``` 안에 넣어서
      바로 복사할 수 있게 출력

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
참고 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
클러스터: {cluster_name}
허브 키워드: {hub_keyword}
Content Type: {content_type}
  → 위 Content Type에 맞는 [1.5단계] content_type별 추가 체크를 반드시 수행하세요.
리서치 단계에서 수집된 원문 URL (참고용):
{url_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
초안
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{draft_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
위 5단계를 순서대로 수행해주세요.
판정 리포트와 정합성 체크는 한국어로, 최종본은 영문 markdown 코드블록으로 출력하세요."""
    return prompt


# =====================================================================
# 명령어
# =====================================================================

def get_next_candidate_fifo():
    """
    Phase 3 자동화용 FIFO 큐 선택.
    오래된 주차의 Grade A → B → C(스킵) 순으로 1개 반환.
    반환: cluster_info dict or None
    """
    data = load_pipeline()
    # 주차 오름차순 (오래된 것 먼저)
    for week in sorted(data.get("weekly_selections", {}).keys()):
        sels = data["weekly_selections"][week]
        # Grade A 우선
        for grade in ("A", "B"):
            for sel in sels:
                if (sel.get("status") == "candidate"
                        and sel.get("data_grade", "") == grade):
                    # selection에 week_tag가 없을 수 있으므로 순회 중인 주차를 주입
                    sel.setdefault("week_tag", week)
                    return sel
    # Grade C는 force 없으면 스킵
    return None


def cmd_next(as_json=False):
    """
    FIFO 큐에서 다음 작성 대상 1건을 조회.
    Step 3 자동화에서 '무엇을 쓸지' 결정하는 진입점.
    --json 지정 시 Actions가 파싱할 수 있는 한 줄 JSON을 출력.
    """
    sel = get_next_candidate_fifo()

    if not sel:
        if as_json:
            print(json.dumps({"ok": False, "reason": "no_candidate"},
                             ensure_ascii=False))
        else:
            print("ℹ️  작성 대기 중인 candidate 없음")
        return None

    cluster_name = sel.get("cluster_name", "")
    content_type = (sel.get("content_type", "") or "").upper()
    payload = {
        "ok":           True,
        "cluster_name": cluster_name,
        "content_type": content_type,
        "data_grade":   sel.get("data_grade", ""),
        "week_tag":     sel.get("week_tag", ""),
        "slug":         slugify(cluster_name),
    }

    if as_json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(f"📌 다음 작성 대상")
        print(f"   클러스터: {cluster_name}")
        print(f"   유형:     {content_type}")
        print(f"   Grade:    {payload['data_grade']}")
        print(f"   주차:     {payload['week_tag']}")

    return payload


def cmd_list():
    data   = load_pipeline()
    weekly = data.get("weekly_selections", {})
    cfg    = load_config()
    tiers  = cfg.get("source_tiers", {})

    print("\n" + "=" * 60)
    print("✍️  글 생성 대기 목록")
    print("=" * 60)

    found = False
    for week, sels in sorted(weekly.items(), reverse=True)[:4]:
        candidates = [s for s in sels if s.get("status") == "candidate"]
        if candidates:
            print(f"\n[{week}]")
            for s in candidates:
                timing      = s.get("timing", "?")
                comp        = s.get("competition_level", "?")
                affiliate   = s.get("affiliate_potential", "?")
                icon        = "🚀" if timing == "PRE-LAUNCH" else "✅" if timing == "NOW" else "⏳"
                print(f"  {icon} {s['cluster_name']}")
                print(f"     유형:{s['content_type']} | 경쟁:{comp} | 어필:{affiliate} | {timing}")
                print(f"     제목: {s.get('suggested_title','')[:55]}")
            found = True

    if not found:
        print("\n  (대기 중인 기획안 없음)")

    paywall_list = tiers.get("paywall", [])
    if paywall_list:
        print(f"\n⛔ 페이월 소스: {', '.join(paywall_list)}")

    if os.path.exists(DRAFTS_DIR):
        drafts = list(Path(DRAFTS_DIR).glob("*.md"))
        if drafts:
            print(f"\n📄 저장된 초안 ({len(drafts)}개):")
            for d in drafts:
                print(f"  • {d.name}")
    print()


def cmd_check_tiers():
    cfg   = load_config()
    tiers = cfg.get("source_tiers", {})
    print("\n" + "=" * 60)
    print("📋 소스 등급 현황 (config.json source_tiers)")
    print("=" * 60)
    for tier, label in [("open","✅ OPEN"), ("paywall","⛔ PAYWALL"), ("title_only","📝 TITLE_ONLY")]:
        lst = tiers.get(tier, [])
        print(f"\n{label} ({len(lst)}개):")
        for s in lst:
            print(f"   • {s}")
    print(f"""
💡 수동 수정: config.json source_tiers
   페이월 해제: paywall → open / 페이월 등록: open → paywall
""")


def cmd_prep(cluster_name, mode="jina", force=False, content_type=None):
    data         = load_pipeline()
    cfg          = load_config()
    cluster_info = find_cluster(data, cluster_name, content_type=content_type)

    if not cluster_info:
        print(f"❌ '{cluster_name}' 클러스터 없음. python write.py list 확인")
        sys.exit(1)

    # Grade C 게이트: Trends/KP 검증이 둘 다 없으면 발행 보류가 원칙
    # (data_grade 필드가 없는 기존 기획안은 통과 — 하위 호환)
    if cluster_info.get("data_grade") == "C" and not force:
        print(f"\n🔴 Grade C — '{cluster_name}'은 Trends/KP 검증 데이터가 없어요.")
        print(f"   원칙: 검색 수요 미확인 상태로는 발행 보류.")
        print(f"   → trends/{get_week_tag()}/ 폴더에 CSV 넣고 분석 후 재시도")
        print(f"   → 급하면 force=True (앱: '미검증 상태로 진행' 체크)")
        return False

    actual_name  = cluster_info.get("cluster_name", cluster_name)
    ct_upper     = (content_type or cluster_info.get("content_type","GUIDE")).upper()
    slug         = slugify(actual_name)
    week_tag     = get_week_tag()

    print(f"\n{'='*60}")
    print(f"✍️  글쓰기 프롬프트 생성: {actual_name}")
    print(f"{'='*60}")
    print(f"  유형: {ct_upper} | "
          f"경쟁: {cluster_info.get('competition_level','?')} | "
          f"timing: {cluster_info.get('timing','?')}")

    # ── HUB 전용: 스포크 MD 파일 자동 로드 ──────────────────────────
    if ct_upper == "HUB":
        print(f"\n  🔷 HUB 모드 — 스포크 글 자동 로드 중...")
        from posts_manager import load_posts
        posts_data = load_posts()

        # hub_keyword → parent_hub → cluster_name → actual_name 순으로 fallback
        hub_keyword = (cluster_info.get("hub_keyword","") or
                       cluster_info.get("parent_hub","") or
                       actual_name)
        parent_hub  = hub_keyword
        print(f"    🔑 허브 키워드: '{hub_keyword}'")
        spoke_articles = []
        for post in posts_data.get("posts", []):
            # hub_cluster 또는 parent_hub 필드로 매칭
            post_hub = (post.get("hub_cluster","") or
                       post.get("parent_hub","")).lower()
            if not post_hub:
                continue
            # 클러스터명 또는 hub_keyword로 매칭
            match_keys = [
                parent_hub.lower(),
                hub_keyword.lower(),
                actual_name.lower(),
            ]
            if not any(post_hub in mk or mk in post_hub for mk in match_keys):
                continue
            # ↑ 매칭 실패 시 스킵, 아래는 매칭 성공 시 실행
            # published/ 폴더에서 MD 파일 찾기 (title/slug 다중 매칭)
            pub_dir    = os.path.join("research_data", "write", "published")
            md_content = ""
            if os.path.exists(pub_dir):
                post_slug = slugify(post.get("title",""))[:40]
                live_slug = post.get("live_url","").split("/")[-2] \
                            if post.get("live_url") else ""
                for fname in sorted(os.listdir(pub_dir)):
                    if not fname.endswith(".md"):
                        continue
                    fname_slug = fname.replace(".md","").lower()
                    if (post_slug[:30] in fname_slug or
                        live_slug[:30] in fname_slug or
                        post.get("id","")[:30] in fname_slug):
                        fpath = os.path.join(pub_dir, fname)
                        md_content = open(fpath, encoding="utf-8").read()
                        break
            spoke_articles.append({
                "title":        post.get("title",""),
                "url":          f"https://frontbuffer.net{post.get('live_url', post.get('url',''))}",
                "content_type": post.get("content_type",""),
                "md_content":   md_content,
            })
            print(f"    ✅ 스포크 로드: {post.get('title','')[:50]} "
                  f"(MD: {'있음' if md_content else '없음'})")

        if not spoke_articles:
            print(f"  ❌ 스포크 글 없음 — posts.json에 {parent_hub} 허브 글이 없어요.")
            return False

        cluster_info["spoke_articles"] = spoke_articles
        # HUB는 외부 소스 수집 불필요 → dummy context
        context_result = {
            "mode": "hub",
            "context_text": "",
            "sources": [],
            "total_ok": len(spoke_articles),
        }
    else:
        # ── 기존 스포크 소스 수집 ────────────────────────────────────
        if mode == "jina":
            context_result = collect_context_multistage(cluster_info, cfg)
        else:
            context_result = collect_context_title(cluster_info)
        print(f"\n  최종 모드: {context_result['mode'].upper()} | "
              f"수집 후보: {context_result.get('total_ok', 0)}개")

    prompt_text      = build_write_prompt(cluster_info, context_result)
    os.makedirs(PROMPTS_DIR, exist_ok=True)
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    content_type_tag = cluster_info.get("content_type", "GUIDE").upper()
    prompt_filename  = f"write_prompt_{slug}_{content_type_tag}_{week_tag}.txt"
    prompt_path      = os.path.join(PROMPTS_DIR, prompt_filename)

    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt_text)

    size_kb = len(prompt_text.encode()) / 1024
    print(f"\n✅ 프롬프트 저장: {prompt_path} ({size_kb:.1f} KB)")

    sources = context_result.get("sources", [])
    if sources:
        print(f"\n📎 소스 현황 (Gemini가 최종 관련성 판단):")
        icons = {"ok":"✅","skipped":"⛔","paywall":"⚠️",
                 "failed":"❌","title_only":"📝","noise":"🔸"}
        for s in sources:
            icon  = icons.get(s.get("status",""), "❓")
            chars = f" ({s.get('chars',0)}자)" if s.get("chars") else ""
            print(f"  {icon} [{s['source']}] {s['title'][:45]}...{chars}")

    draft_fname = f"{slug}_{content_type_tag}.md"
    print(f"""
다음 단계:
  1. prompts/{prompt_filename} → Gemini 웹 붙여넣기
     (Gemini가 관련 소스만 골라 쓰고, 사용/폐기 목록을 맨 위에 보고함)
  2. 초안 받기 → drafts/{draft_fname} 저장
  3. python write.py review "{actual_name}" --type {content_type_tag}
""")


def cmd_review(cluster_name, content_type=None):
    data         = load_pipeline()
    cluster_info = find_cluster(data, cluster_name, content_type=content_type)
    if not cluster_info:
        print(f"❌ '{cluster_name}' 클러스터 없음")
        sys.exit(1)

    actual_name = cluster_info.get("cluster_name", cluster_name)
    slug        = slugify(actual_name)
    _ct_tag     = (content_type or cluster_info.get("content_type", "")).upper().strip()
    draft_fname = f"{slug}_{_ct_tag}.md" if _ct_tag else f"{slug}.md"
    draft_path  = os.path.join(DRAFTS_DIR, draft_fname)

    print(f"\n{'='*60}")
    print(f"🔍 검증+수정 프롬프트 생성: {actual_name}")
    print(f"{'='*60}")

    if not os.path.exists(draft_path):
        print(f"❌ 초안 없음: {draft_path}")
        print(f"   Gemini 초안을 drafts/{slug}.md 에 저장 후 재실행하세요.")
        sys.exit(1)

    with open(draft_path, encoding="utf-8") as f:
        draft_text = f.read()

    word_count  = len(draft_text.split())
    review_text = build_review_prompt(cluster_info, draft_text)

    os.makedirs(PROMPTS_DIR, exist_ok=True)
    os.makedirs(FINAL_DIR, exist_ok=True)
    _ct_tag = (content_type or "").upper().strip()
    review_fname = (f"review_prompt_{slug}_{_ct_tag}.txt" if _ct_tag else f"review_prompt_{slug}.txt")
    review_path = os.path.join(PROMPTS_DIR, review_fname)
    with open(review_path, "w", encoding="utf-8") as f:
        f.write(review_text)

    print(f"  초안: {word_count}단어")
    print(f"✅ 검증+수정 프롬프트: {review_path} ({len(review_text.encode())/1024:.1f} KB)")

    # ── HUB: 초안을 final/에 복사 (Claude 최종본 붙여넣기 기준 파일로 사용)
    # 스포크는 외부 팩트체크가 필요해서 Claude가 수정 후 수동 저장하지만,
    # HUB는 구조/링크 검증이 중심이라 초안을 final/에 미리 복사해두고
    # Claude 최종본으로 덮어쓰는 방식을 사용.
    if cluster_info.get("content_type", "").upper() == "HUB":
        os.makedirs(FINAL_DIR, exist_ok=True)
        final_fname = f"{slug}_HUB.md"
        final_path  = os.path.join(FINAL_DIR, final_fname)
        if not os.path.exists(final_path):
            import shutil
            shutil.copy2(draft_path, final_path)
            print(f"  📋 HUB 초안 → final/{final_fname} 복사 완료")
            print(f"     Claude 최종본으로 이 파일을 덮어쓰세요.")
        else:
            print(f"  ℹ️  final/{final_fname} 이미 존재 — 덮어쓰지 않음")
            print(f"     최종본으로 교체하려면 해당 파일을 직접 수정하세요.")
        print(f"""
다음 단계:
  1. prompts/{review_fname} → Claude 대화창에 붙여넣기
     (Claude가 구조·링크·독자경험 검증 + 최종본 출력)
  2. Claude가 출력한 최종본(markdown 코드블록)을
     final/{final_fname} 에 붙여넣어 저장 (덮어쓰기)
  3. python write.py done "{actual_name}" --type HUB
""")
    else:
        print(f"""
다음 단계:
  1. prompts/{review_fname} → Claude 대화창에 붙여넣기
     (Claude가 웹검색으로 팩트 검증 + 수정 최종본까지 한 번에 출력)
  2. Claude가 출력한 최종본(markdown 코드블록)을
     final/{slug}_{_ct_tag}.md 에 저장
  3. python write.py done "{actual_name}"
""")



# =====================================================================
# 품질 게이트 + 폐기 처리
# =====================================================================

def check_draft_quality(draft_text):
    """초안 품질 자동 검사. Phase 3 자동화에서도 동일 함수 사용."""
    import re
    errors   = []
    warnings = []
    if "[SOURCES USED: None]" in draft_text:
        errors.append("소스 없음 — [SOURCES USED: None] 감지")
    if "NO RELEVANT SOURCES" in draft_text:
        errors.append("관련 소스 없음 — [NO RELEVANT SOURCES] 감지")
    nv_count = len(re.findall(r"\[NEEDS VERIFICATION\]", draft_text))
    if nv_count >= 3:
        errors.append(f"[NEEDS VERIFICATION] {nv_count}개 — 3개 이상 발행 금지")
    elif nv_count > 0:
        warnings.append(f"[NEEDS VERIFICATION] {nv_count}개 — review에서 해결 필요")
    word_count = len(draft_text.split())
    if word_count < 600:
        errors.append(f"단어 수 {word_count}개 — 600 미만 (재작성 필요)")
    elif word_count < 800:
        warnings.append(f"단어 수 {word_count}개 — 800 미만 (review에서 보강 필요)")
    risky = ["bypass.*drm", "drm.*bypass", "crack.*launcher",
             "launcher.*bypass", "remove.*drm"]
    for pat in risky:
        if re.search(pat, draft_text.lower()):
            errors.append("법적 위험 콘텐츠 감지 — DRM 우회 패턴")
            break
    return {"ok": len(errors) == 0, "errors": errors,
            "warnings": warnings, "nv_count": nv_count, "word_count": word_count}


def get_content_filename(slug, content_type=""):
    """draft/final 파일명: {slug}_{TYPE}.md."""
    ct = (content_type or "").upper().strip()
    return f"{slug}_{ct}.md" if ct else f"{slug}.md"


def discard_cluster(cluster_name, content_type=None, reason="품질 게이트 실패"):
    """기획안 폐기. content_type 지정 시 해당 type만 폐기."""
    data = load_pipeline()
    discarded = False
    for week_sels in data.get("weekly_selections", {}).values():
        for s in week_sels:
            name_match = s.get("cluster_name") == cluster_name
            type_match = (content_type is None or
                          s.get("content_type", "").upper() == content_type.upper())
            if name_match and type_match and s.get("status") == "candidate":
                s["status"]         = "discarded"
                s["discarded_at"]   = datetime.now(timezone.utc).isoformat()
                s["discard_reason"] = reason
                discarded = True
    if discarded:
        save_pipeline(data)
    return discarded


def record_publish(cluster_name, title, url, content_type=None):
    """
    발행 완료 기록 — 비대화형 코어.
    Streamlit/GitHub Actions에서 직접 호출 가능.
    반환: dict (ok, error/통계)
    """
    data         = load_pipeline()
    cluster_info = find_cluster(data, cluster_name, content_type)
    if not cluster_info:
        return {"ok": False, "error": f"'{cluster_name}' 클러스터 없음"}

    _ct_pub = (content_type or cluster_info.get("content_type", "")).upper().strip()

    actual_name  = cluster_info.get("cluster_name", cluster_name)
    # 발행 기록 content_type: 호출자 지정 우선 (_ct_pub 이미 정규화됨)
    content_type = _ct_pub or cluster_info.get("content_type", "")
    now          = datetime.now(timezone.utc)
    week_tag     = now.strftime("%Y-W%W")

    # ── 중복 발행 방지: 같은 cluster + content_type이 이미 발행됐으면 스킵 ──
    _already = any(
        p.get("cluster_name") == actual_name
        and (p.get("content_type", "") or "").upper() == (content_type or "").upper()
        for p in data.get("published", [])
    )
    if _already:
        return {"ok": False,
                "error": f"이미 발행 기록됨: {actual_name} ({content_type})"}

    data.setdefault("published", []).append({
        "cluster_name": actual_name, "title": title, "url": url,
        "content_type": content_type, "week_tag": week_tag,
        "published_at": now.isoformat(),
        "hub_cluster":  cluster_info.get("parent_hub", ""),
    })

    TYPE_SEQUENCE = ["COMPARISON", "GUIDE", "EXPLAINER", "LISTICLE"]
    if actual_name in data.get("covered_clusters", {}):
        cc = data["covered_clusters"][actual_name]
        if content_type and content_type not in cc.get("types_done", []):
            cc.setdefault("types_done", []).append(content_type)
        done = set(cc.get("types_done", []))
        cc["suggest_next"] = [t for t in TYPE_SEQUENCE if t not in done]
        cc["last_week"]    = week_tag

    # hub_clusters spoke_urls 업데이트 (발행 시 자동 연결)
    if "hub_clusters" not in data:
        data["hub_clusters"] = {}
    parent_hub = cluster_info.get("parent_hub", "")
    if parent_hub and parent_hub in data.get("hub_clusters", {}):
        hc = data["hub_clusters"][parent_hub]
        hc.setdefault("spoke_urls", {})
        # content_type 포함 키로 저장 (같은 클러스터 GUIDE/COMPARISON 구분)
        _spoke_key = (f"{actual_name} ({_ct_pub})" if _ct_pub else actual_name)
        hc["spoke_urls"][_spoke_key] = url
        hc["internal_links"] = list(hc["spoke_urls"].values())
        if len(hc["spoke_urls"]) >= 2 and hc.get("hub_status") in ("PENDING", "READY"):
            hc["hub_status"] = "READY"

    # 모든 주차에서 해당 기획안 탐색 (기획/발행 주차 불일치 대응)
    # content_type 정규화 비교 (대소문자/None 안전)
    updated_week = None
    for week, sels in sorted(data.get("weekly_selections", {}).items(), reverse=True):
        for sel in sels:
            _sel_ct = (sel.get("content_type", "") or "").upper().strip()
            _match_ct = (not _ct_pub) or (_sel_ct == _ct_pub)
            if (sel.get("cluster_name") == actual_name
                    and _match_ct
                    and sel.get("status") != "published"):
                sel["status"] = "published"
                sel["url"]    = url
                updated_week  = week
                break
        if updated_week:
            break

    save_pipeline(data)

    # 발행 아카이브: final/{slug}_{TYPE}.md → published/YYYY-MM-DD-{slug}_{TYPE}.md
    # (Jekyll _posts 규격 파일명 — 블로그 세팅 시 그대로 복사 가능, 누적 저장)
    archived_path = None
    _final_fname = (f"{slugify(actual_name)}_{_ct_pub}.md" if _ct_pub
                    else f"{slugify(actual_name)}.md")
    final_path = os.path.join(FINAL_DIR, _final_fname)
    # 구버전 파일명 fallback
    if not os.path.exists(final_path):
        _legacy = os.path.join(FINAL_DIR, f"{slugify(actual_name)}.md")
        if os.path.exists(_legacy):
            final_path = _legacy
            _final_fname = f"{slugify(actual_name)}.md"
    if os.path.exists(final_path):
        os.makedirs(PUBLISHED_DIR, exist_ok=True)
        date_prefix   = now.strftime("%Y-%m-%d")
        archived_name = f"{date_prefix}-{_final_fname}"
        archived_path = os.path.join(PUBLISHED_DIR, archived_name)
        if not os.path.exists(archived_path):
            md_text = open(final_path, encoding="utf-8").read()

            # 카테고리 자동 분류
            _gaming_keys = ["steam", "game", "gaming", "xbox", "playstation",
                            "nintendo", "assassin", "valve"]
            _cat = "gaming" if any(k in actual_name.lower() for k in _gaming_keys) else "tech"

            # 태그 자동 생성 — content_type별로 다르게 구성해 카니발라이제이션 방지
            _hub = cluster_info.get("hub_keyword", "").lower()
            _content_type_val = cluster_info.get("content_type", "GUIDE")
            _spoke_all = [k.lower() for k in cluster_info.get("spoke_keywords", [])]

            # 제목에서 실제 사용된 명사구 추출 (H1/title 기준, 최대 2개)
            _title_words = re.findall(r'\b[a-zA-Z]{4,}\b', title.lower())
            _title_tags = [w for w in _title_words
                           if w not in ("with", "your", "what", "when", "before",
                                        "chrome", "extensions", "extension")][:2]

            # content_type별로 spoke_keywords 슬라이스를 다르게 선택 (겹침 최소화)
            _type_offset = {"GUIDE": 0, "LISTICLE": 2, "COMPARISON": 1, "EXPLAINER": 3}
            _offset = _type_offset.get(_content_type_val, 0)
            _spoke_slice = (_spoke_all[_offset:_offset+2] if len(_spoke_all) > _offset
                            else _spoke_all[:2])

            _tags = [_hub, _content_type_val.lower()] + _spoke_slice + _title_tags
            _tags = list(dict.fromkeys(t for t in _tags if t))[:6]  # 중복 제거, 최대 6개
            _tags_str = ", ".join(f'"{t}"' for t in _tags)

            # excerpt: 본문 첫 문단 (front matter/H1 제외, 150자)
            import re as _re
            _body_lines = [l for l in md_text.splitlines()
                           if l.strip() and not l.startswith("#")
                           and not l.startswith("[SOURCES") and not l.startswith("[DISCARDED")]
            if _body_lines:
                _raw = _body_lines[0].replace('"', "'")
                if len(_raw) > 150:
                    # 150자 근처 마지막 공백에서 자르고 … 추가
                    _cut = _raw[:150].rsplit(" ", 1)[0]
                    _excerpt = _cut + "…"
                else:
                    _excerpt = _raw
            else:
                _excerpt = ""

            front_matter = f"""---
layout: single
title: "{title.replace('"', "'")}"
date: {now.strftime("%Y-%m-%d %H:%M:%S")} +0900
categories: [{_cat}]
tags: [{_tags_str}]
excerpt: "{_excerpt}"
author_profile: false
read_time: true
share: true
---

"""
            # H1 + SOURCES USED/DISCARDED 헤더 제거
            md_body = _re.sub(r'^# .+\n', '', md_text, count=1, flags=_re.MULTILINE)
            md_body = _re.sub(r'^\[SOURCES USED:.*\]\n?', '', md_body, flags=_re.MULTILINE)
            md_body = _re.sub(r'^\[DISCARDED:.*\]\n?', '', md_body, flags=_re.MULTILINE)

            with open(archived_path, "w", encoding="utf-8") as _f:
                _f.write(front_matter + md_body.lstrip())

    # posts.json 등록 (독립 글 목록)
    if _POSTS_MANAGER_OK:
        try:
            register_post(cluster_info, title, url,
                          published_date=now.strftime("%Y-%m-%d"))
        except Exception as e:
            print(f"⚠️ posts.json 등록 실패 (무시): {e}")

    return {
        "ok":              True,
        "title":           title,
        "url":             url,
        "actual_name":     actual_name,
        "week_tag":        week_tag,
        "updated_week":    updated_week,
        "archived":        archived_path,
        "published_count": len(data.get("published", [])),
        "completed":       sum(1 for c in data.get("covered_clusters", {}).values()
                               if len(c.get("types_done", [])) >= 2),
    }


def cmd_done(cluster_name, title=None, url=None, content_type=None):
    """
    CLI 래퍼 — 인자 없으면 대화형 입력 (기존 호환).
    Actions에서는 --title/--url/--type을 모두 넘겨 비대화형으로 실행.
    """
    print(f"\n{'='*60}")
    _ct_label = f" [{content_type.upper()}]" if content_type else ""
    print(f"📤 발행 완료 기록: {cluster_name}{_ct_label}")
    print(f"{'='*60}")

    if not title:
        title = input("  실제 발행 제목: ").strip()
    if not url:
        url = input("  발행 URL: ").strip()

    result = record_publish(cluster_name, title, url,
                            content_type=content_type)

    if not result["ok"]:
        print(f"❌ {result['error']}")
        sys.exit(1)

    if result["updated_week"] and result["updated_week"] != result["week_tag"]:
        print(f"  ℹ️  기획 주차 {result['updated_week']} → 발행 주차 {result['week_tag']}")
    elif not result["updated_week"]:
        print(f"  ⚠️  weekly_selections에서 기획안을 찾지 못함 (published 기록은 저장됨)")

    print(f"\n✅ 발행 완료: {result['title']}")
    print(f"📊 내부 자산: 발행 {result['published_count']}편 | "
          f"완결 클러스터 {result['completed']}개\n")


# =====================================================================
# 메인
# =====================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="LIFO-LIKE 글 생성 파이프라인 v5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python write.py list
  python write.py check-tiers
  python write.py prep "Steam Deck Windows Compatibility"
  python write.py prep "Steam Deck Windows Compatibility" --mode title
  python write.py review "Steam Deck Windows Compatibility"
  python write.py done "Steam Deck Windows Compatibility"
        """
    )
    parser.add_argument("command",
                        choices=["list","prep","review","done","check-tiers","next"])
    parser.add_argument("cluster", nargs="?", default="")
    parser.add_argument("--mode", choices=["jina","title"], default="jina")
    parser.add_argument("--title", default=None, help="발행 제목 (done용, 자동화 시)")
    parser.add_argument("--url", default=None, help="발행 URL (done용, 자동화 시)")
    parser.add_argument("--type", dest="content_type", default=None,
                        help="content_type 지정 (GUIDE/LISTICLE/COMPARISON/EXPLAINER/HUB)")
    parser.add_argument("--json", action="store_true",
                        help="결과를 JSON으로 출력 (Actions 파싱용)")
    args = parser.parse_args()

    if args.command == "list":
        cmd_list()
    elif args.command == "check-tiers":
        cmd_check_tiers()
    elif args.command == "next":
        cmd_next(as_json=args.json)
    elif args.command == "prep":
        if not args.cluster:
            print("❌ 클러스터명 입력하세요.")
            sys.exit(1)
        cmd_prep(args.cluster, mode=args.mode, content_type=args.content_type)
    elif args.command == "review":
        if not args.cluster:
            print("❌ 클러스터명 입력하세요.")
            sys.exit(1)
        cmd_review(args.cluster, content_type=args.content_type)
    elif args.command == "done":
        if not args.cluster:
            print("❌ 클러스터명 입력하세요.")
            sys.exit(1)
        cmd_done(args.cluster, title=args.title, url=args.url,
                 content_type=args.content_type)
