# =====================================================================
# 🌱 seed_inject.py — 개별 주제 추가 (Step 2-1)
# =====================================================================
# 역할: 주제 키워드를 받아서
#       1. Google News RSS로 관련 기사 수집
#       2. Gemini 기획 프롬프트 생성
#       3. Gemini API 호출 → 클러스터 기획
#       4. content_pipeline.json에 append
#
# 사용법:
#   python seed_inject.py "RTX 5090 vs RTX 4090" "Android 16 features"
#   python seed_inject.py --topics "RTX 5090, Android 16" --types "GUIDE,COMPARISON"
# =====================================================================

import os
import re
import sys
import json
import time
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

import requests

# ── 경로 설정 ──
PIPELINE_FILE = "content_pipeline.json"
CONFIG_FILE   = "config.json"
OUTPUT_DIR    = "research_data"
WRITE_DIR     = os.path.join(OUTPUT_DIR, "write")

# ── Gemini 설정 ──
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL     = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={{api_key}}"
)
MAX_RETRIES  = 3
RETRY_DELAY  = 10
JINA_BASE    = "https://r.jina.ai/"
JINA_MAX_CHARS = 2000

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

# ── Content Type 기본 배분 ──
DEFAULT_TYPES = ["GUIDE", "COMPARISON", "EXPLAINER"]


def get_week_tag():
    return datetime.now(timezone.utc).strftime("%Y-W%W")


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def load_pipeline():
    try:
        return json.loads(open(PIPELINE_FILE, encoding="utf-8").read())
    except FileNotFoundError:
        return {"weekly_selections": {}, "covered_clusters": {}, "published": []}


def save_pipeline(data):
    data["_last_updated"] = datetime.now(timezone.utc).isoformat()
    open(PIPELINE_FILE, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=2)
    )


def get_already_covered(pipeline):
    """이미 다룬 클러스터 목록 추출"""
    covered = set()
    for week, sels in pipeline.get("weekly_selections", {}).items():
        for sel in sels:
            if sel.get("status") != "rejected":
                covered.add(sel.get("cluster_name", "").lower())
    for name in pipeline.get("covered_clusters", {}).keys():
        covered.add(name.lower())
    return covered


def fetch_google_news_rss(topic, max_items=5):
    """Google News RSS에서 주제 관련 기사 수집"""
    url = f"https://news.google.com/rss/search?q={quote_plus(topic)}&hl=en-US&gl=US&ceid=US:en"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"    ⚠️ RSS 오류 {resp.status_code}")
            return []

        root = ET.fromstring(resp.text)
        items = []
        for item in root.findall(".//item")[:max_items]:
            title = item.findtext("title", "").strip()
            link  = item.findtext("link", "").strip()
            desc  = item.findtext("description", "").strip()
            source = item.findtext("source", "").strip()
            if title:
                items.append({
                    "title":  title,
                    "url":    link,
                    "desc":   re.sub(r"<[^>]+>", "", desc)[:200],
                    "source": source,
                })
        return items
    except Exception as e:
        print(f"    ⚠️ RSS 수집 실패: {e}")
        return []


def fetch_article_content(url):
    """Jina로 기사 본문 수집"""
    try:
        resp = requests.get(f"{JINA_BASE}{url}", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.text.strip()[:JINA_MAX_CHARS]
    except Exception:
        pass
    return ""


def build_seed_prompt(topics_data, covered_clusters, pipeline, content_types):
    """시드 기반 Gemini 프롬프트 생성"""
    week_tag = get_week_tag()

    # 이미 발행된 클러스터 목록
    covered_list = "\n".join(f"  - {c}" for c in sorted(covered_clusters)[:30]) or "  (없음)"

    # content_pipeline 현재 candidate 목록
    current_week = pipeline.get("weekly_selections", {}).get(week_tag, [])
    current_list = "\n".join(
        f"  - {s.get('cluster_name')} [{s.get('content_type')}]"
        for s in current_week if s.get("status") == "candidate"
    ) or "  (없음)"

    # 주제별 수집 데이터
    topics_section = ""
    for topic, articles in topics_data.items():
        topics_section += f"\n### 주제: {topic}\n"
        if articles:
            for a in articles:
                topics_section += f"  - [{a['source']}] {a['title']}\n"
                if a.get("desc"):
                    topics_section += f"    {a['desc'][:100]}\n"
        else:
            topics_section += "  (기사 수집 실패 — 키워드만으로 기획)\n"

    # content_type 배분 지시
    types_instruction = ""
    if content_types:
        types_instruction = f"\n각 주제의 content_type은 다음 중에서 선택: {', '.join(content_types)}\n"

    prompt = f"""You are a content strategist for Frontbuffer Editorial, a tech and gaming blog targeting English-speaking readers.

## TASK
The editor has manually selected the following topics to cover this week.
Generate a content plan for EACH topic below.

## MANUALLY SELECTED TOPICS WITH NEWS CONTEXT
{topics_section}

## CONTENT TYPES AVAILABLE
- GUIDE: How-to, step-by-step instructions
- COMPARISON: Side-by-side analysis of 2-3 options
- EXPLAINER: What/why/how explanation of a concept
- LISTICLE: Ranked or categorized list
- HUB: Pillar page linking to spoke articles (only if 2+ spokes already exist)
{types_instruction}

## ALREADY COVERED (DO NOT REPEAT)
{covered_list}

## CURRENTLY IN PIPELINE THIS WEEK (DO NOT DUPLICATE)
{current_list}

## RULES
1. Generate EXACTLY ONE cluster entry per topic provided
2. Each cluster must have a unique angle not already covered above
3. Focus on evergreen value — avoid pure news recaps
4. hub_keyword should be the main SEO keyword (1-3 words)
5. spoke_keywords: 3-5 related long-tail keywords
6. assign content_type based on the topic's best format
7. Set data_grade: "A" for all (manually selected = trusted)
8. folder: leave empty string ""

## OUTPUT FORMAT
Return ONLY a JSON array. No explanation. No markdown fences.

[
  {{
    "cluster_name": "RTX 5090 vs RTX 4090 Performance",
    "content_type": "COMPARISON",
    "hub_keyword": "RTX 5090",
    "spoke_keywords": ["rtx 5090 benchmark", "rtx 5090 vs 4090 gaming", "rtx 5090 price performance"],
    "rationale": "High search intent for GPU comparison, evergreen as long as cards are available",
    "data_grade": "A",
    "trends_pattern": "RISING",
    "folder": "",
    "source": "seed_inject"
  }}
]"""
    return prompt


def call_gemini(prompt_text):
    """Gemini API 호출"""
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY 없음")
        sys.exit(1)

    url     = GEMINI_URL.format(api_key=GEMINI_API_KEY)
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "temperature":     0.4,
            "maxOutputTokens": 4096,
        }
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"  🤖 Gemini 호출 중... (시도 {attempt}/{MAX_RETRIES})")
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
    """Gemini 응답에서 JSON 파싱"""
    text = re.sub(r"```json|```", "", text).strip()
    # 배열 추출
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


def get_next_publish_order(pipeline, week_tag):
    """final/ + pipeline 기준으로 다음 publish_order 계산"""
    _final_dir = os.path.join("research_data", "write", "final")
    _max_order = 0
    if os.path.isdir(_final_dir):
        for _f in Path(_final_dir).glob("*.md"):
            if _f.name.startswith("review_report_"):
                continue
            _prefix = _f.name.split("_")[0]
            try:
                _max_order = max(_max_order, int(_prefix))
            except ValueError:
                pass

    # pipeline에서도 확인
    for sel in pipeline.get("weekly_selections", {}).get(week_tag, []):
        try:
            _max_order = max(_max_order, int(sel.get("publish_order", 0)))
        except (ValueError, TypeError):
            pass

    return _max_order + 1


def main():
    parser = argparse.ArgumentParser(description="Step 2-1: 개별 주제 추가")
    parser.add_argument("topics", nargs="*", help="주제 키워드 (복수 가능)")
    parser.add_argument("--topics", dest="topics_str", default="",
                        help="콤마 구분 주제 (예: 'RTX 5090, Android 16')")
    parser.add_argument("--types", default="",
                        help="content_type 지정 (예: 'GUIDE,COMPARISON')")
    parser.add_argument("--week", default=None, help="주차 태그 (기본: 현재 주)")
    args = parser.parse_args()

    # 주제 파싱
    topics = list(args.topics or [])
    if args.topics_str:
        topics += [t.strip() for t in args.topics_str.split(",") if t.strip()]
    topics = list(dict.fromkeys(topics))  # 중복 제거

    if not topics:
        print("❌ 주제를 입력하세요.")
        print("   예: python seed_inject.py 'RTX 5090 vs RTX 4090' 'Android 16'")
        sys.exit(1)

    # content_type 파싱
    content_types = [t.strip().upper() for t in args.types.split(",") if t.strip()] \
                    if args.types else DEFAULT_TYPES

    week_tag = args.week or get_week_tag()

    print("=" * 60)
    print(f"🌱 Step 2-1: 개별 주제 추가")
    print("=" * 60)
    print(f"  주차: {week_tag}")
    print(f"  주제: {topics}")
    print(f"  타입: {content_types}")

    # 파이프라인 로드
    pipeline = load_pipeline()
    covered  = get_already_covered(pipeline)
    print(f"  기존 클러스터: {len(covered)}개")

    # ── Step 1: Google News RSS 수집 ──
    print(f"\n{'─'*40}")
    print(f"📰 Google News RSS 수집")
    topics_data = {}
    for topic in topics:
        print(f"  🔍 '{topic}' 검색 중...")
        articles = fetch_google_news_rss(topic, max_items=5)
        topics_data[topic] = articles
        print(f"    → {len(articles)}개 기사 수집")
        for a in articles[:3]:
            print(f"      [{a['source']}] {a['title'][:60]}")
        time.sleep(1)  # rate limit 방지

    # ── Step 2: Gemini 프롬프트 생성 + 호출 ──
    print(f"\n{'─'*40}")
    print(f"🤖 Gemini 기획 생성")
    prompt = build_seed_prompt(topics_data, covered, pipeline, content_types)

    # 프롬프트 저장 (디버깅용)
    prompt_dir  = os.path.join(OUTPUT_DIR, "weekly", week_tag)
    os.makedirs(prompt_dir, exist_ok=True)
    prompt_path = os.path.join(prompt_dir, f"seed_inject_prompt_{int(time.time())}.txt")
    open(prompt_path, "w", encoding="utf-8").write(prompt)
    print(f"  📄 프롬프트 저장: {prompt_path}")

    response = call_gemini(prompt)
    if not response:
        print("❌ Gemini 응답 없음")
        sys.exit(1)

    # ── Step 3: JSON 파싱 ──
    selections = parse_json_response(response)
    if not selections:
        print("❌ 기획안 파싱 실패")
        raw_path = os.path.join(prompt_dir, f"seed_inject_raw_{int(time.time())}.txt")
        open(raw_path, "w", encoding="utf-8").write(response)
        print(f"   원문 저장: {raw_path}")
        sys.exit(1)

    print(f"  ✅ {len(selections)}개 기획안 생성")

    # ── Step 4: 중복 체크 + publish_order 부여 ──
    next_order = get_next_publish_order(pipeline, week_tag)
    now        = datetime.now(timezone.utc)
    added      = []

    for sel in selections:
        cluster_name = sel.get("cluster_name", "").strip()
        if not cluster_name:
            continue

        # 중복 체크
        if cluster_name.lower() in covered:
            print(f"  ⏭️  중복 스킵: {cluster_name}")
            continue

        # 필수 필드 보완
        sel.setdefault("content_type", "GUIDE")
        sel.setdefault("data_grade", "A")
        sel.setdefault("trends_pattern", "STABLE")
        sel.setdefault("hub_keyword", slugify(cluster_name))
        sel.setdefault("spoke_keywords", [])
        sel.setdefault("folder", "")
        sel["publish_order"] = next_order
        sel["status"]        = "candidate"
        sel["week_tag"]      = week_tag
        sel["selected_at"]   = now.isoformat()
        sel["source"]        = "seed_inject"

        next_order += 1
        added.append(sel)
        print(f"  ✅ 추가: [{sel['publish_order']:03d}] {cluster_name} [{sel['content_type']}]")

    if not added:
        print("⚠️  추가된 클러스터 없음 (모두 중복)")
        sys.exit(0)

    # ── Step 5: content_pipeline.json에 append ──
    week_sels = pipeline.setdefault("weekly_selections", {}).setdefault(week_tag, [])
    week_sels.extend(added)
    save_pipeline(pipeline)
    print(f"\n✅ content_pipeline.json 업데이트: {len(added)}개 추가")

    # ── Step 6: 결과 출력 ──
    print(f"\n{'='*60}")
    print(f"🎯 추가 완료: {len(added)}개")
    for s in added:
        print(f"  [{s['publish_order']:03d}] [{s['data_grade']}][{s['content_type']}] {s['cluster_name']}")
    print(f"\n다음 단계: Step 3 트리거 → 글 생성 시작")


if __name__ == "__main__":
    main()
