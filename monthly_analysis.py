# =====================================================================
# 📅 월간 패턴 분석 (monthly_analysis.py)
# =====================================================================
# 목적: 주간 raw_research_log 4개를 합산해서
#       "매주 반복 등장한 주제"를 찾아냄 → 진짜 에버그린 확인
# 실행: python monthly_analysis.py  (월 1회, 4주치 쌓인 후)
# 설정: config.json
# 출력:
#   research_data/monthly_report_YYYY-MM.md
# =====================================================================

import os
import re
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone

with open("config.json", encoding="utf-8") as f:
    CFG = json.load(f)

OUTPUT_DIR      = CFG["output_dir"]
WEEKS_TO_USE    = CFG["monthly"]["weeks_to_aggregate"]   # 기본 4
MIN_WEEKS       = CFG["monthly"]["min_weeks_to_qualify"] # 기본 3
FREQ_CFG        = CFG["frequency"]

STOPWORDS = {
    'the','a','an','is','are','was','were','be','been','to','of',
    'in','for','on','with','at','by','from','and','or','but','as',
    'it','its','this','that','new','now','will','has','have','had',
    'you','your','more','get','gets','how','why','what','when','who',
    'can','could','should','would','may','might','just','about',
    'says','said','reports','update','news','still','also',
    'reportedly','than','off','make','even','later','like','back',
    'made','set','drops','finally','latest','via','after','i',
}


def load_weekly_logs():
    """최근 N주치 raw_research_log를 로드합니다."""
    weekly_dir = os.path.join(OUTPUT_DIR, "weekly")
    if not os.path.isdir(weekly_dir):
        return []
    # weekly/YYYY-WW/raw_research_log.json 패턴
    logs = sorted([
        d for d in os.listdir(weekly_dir)
        if os.path.isdir(os.path.join(weekly_dir, d))
        and os.path.exists(os.path.join(weekly_dir, d, "raw_research_log.json"))
    ], reverse=True)[:WEEKS_TO_USE]

    if not logs:
        print("⚠️ 주간 로그 파일이 없습니다.")
        return []

    weeks = []
    for log_file in reversed(logs):  # 오래된 것부터
        path = os.path.join(OUTPUT_DIR, "weekly", log_file, "raw_research_log.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        weeks.append({
            "week_tag": data.get("week_tag", log_file),
            "items":    data.get("items", []),
        })
        print(f"  • 로드: {log_file} ({len(data.get('items',[]))}건)")

    return weeks


def extract_keywords(title):
    words = re.sub(r"[^\w\s'-]", " ", title.lower()).split()
    out   = []
    for w in words:
        w = w.strip("'-")
        if not w or w in STOPWORDS or len(w) <= 2 or w.isdigit():
            continue
        out.append(w)
    return out


def analyze_patterns(weeks):
    """
    주차별 키워드 집합을 비교해서
    MIN_WEEKS 이상 등장한 키워드 = 지속 패턴으로 분류합니다.
    """
    # 주차별 키워드 빈도
    weekly_counters = []
    for week in weeks:
        counter = Counter()
        for it in week["items"]:
            kws = extract_keywords(it["title"])
            counter.update(kws)
            counter.update(f"{a} {b}" for a, b in zip(kws, kws[1:]))
        weekly_counters.append(counter)

    # 전체 합산 빈도
    total = Counter()
    for c in weekly_counters:
        total.update(c)

    # 몇 주에 걸쳐 등장했는지 카운트
    week_appearance = Counter()
    for c in weekly_counters:
        for kw in c:
            if c[kw] >= 1:
                week_appearance[kw] += 1

    # 분류
    persistent = {kw: total[kw] for kw in week_appearance
                  if week_appearance[kw] >= MIN_WEEKS}
    occasional = {kw: total[kw] for kw in week_appearance
                  if week_appearance[kw] < MIN_WEEKS and total[kw] >= 3}

    return total, week_appearance, persistent, occasional


def build_monthly_report(weeks, total, week_appearance, persistent, occasional):
    now_str  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    month    = datetime.now(timezone.utc).strftime("%Y-%m")
    week_tags = [w["week_tag"] for w in weeks]
    total_items = sum(len(w["items"]) for w in weeks)

    # 지속 패턴 상위 키워드 (단어 + 2단어 조합 분리)
    persistent_words  = sorted([(k,v) for k,v in persistent.items() if " " not in k],
                                key=lambda x: -x[1])[:40]
    persistent_bigrams = sorted([(k,v) for k,v in persistent.items() if " " in k],
                                key=lambda x: -x[1])[:20]

    kw_persistent_lines = "\n".join(
        f"  {w} (총 {c}회, {week_appearance[w]}주 연속)" for w,c in persistent_words
    )
    bi_persistent_lines = "\n".join(
        f"  {w} (총 {c}회, {week_appearance[w]}주 연속)" for w,c in persistent_bigrams
    )

    # 월간 프롬프트 — 주간보다 엄격한 기준
    prompt_block = f"""You are a content strategist for Frontbuffer Editorial, an independent tech/gaming media brand.
This is a MONTHLY analysis based on {len(weeks)} weeks of data — use a STRICTER evergreen standard than weekly analysis.

CONTEXT:
- Data period: {', '.join(week_tags)}
- Total items analyzed: {total_items}
- Only keywords appearing in {MIN_WEEKS}+ out of {len(weeks)} weeks are shown below
- These are topics that have sustained presence, NOT one-week spikes

CORE PRINCIPLE (stricter than weekly):
- Evergreen here means: people searched for this EVERY week for a month
- Topics appearing only 1-2 weeks = almost certainly NEWS_ONLY, exclude them
- Focus on durable search demand: comparisons, guides, explainers people return to
- High affiliate potential is a strong bonus

PERSISTENT KEYWORDS ({MIN_WEEKS}+ weeks out of {len(weeks)}):

[단어]
{kw_persistent_lines}

[2단어 조합]
{bi_persistent_lines}

TASKS:
1. Identify 5-8 HIGH-CONFIDENCE evergreen clusters from these persistent keywords
2. For each cluster:
   - content_type: COMPARISON / GUIDE / EXPLAINER / LISTICLE
     (NO NEWS_ONLY here — persistent topics should all be actionable)
   - suggested_title: specific, searchable English blog title
   - evergreen_score: 0-100 (monthly standard — be strict, 70+ only)
   - affiliate_potential: HIGH / MEDIUM / LOW
   - timing: NOW / PRE-LAUNCH / WAIT
   - content_series: Could this become a series? (true/false)
   - trends_queries: 1-2 search terms for Google Trends validation
   - reasoning: 2-3 sentences in Korean — why this persisted for a month

OUTPUT FORMAT — respond ONLY with this JSON array:
[
  {{
    "cluster_name": "...",
    "content_type": "COMPARISON",
    "suggested_title": "...",
    "evergreen_score": 85,
    "affiliate_potential": "HIGH",
    "timing": "NOW",
    "content_series": false,
    "trends_queries": ["...", "..."],
    "reasoning": "..."
  }}
]

RULES:
- Only use keywords from the provided persistent list
- evergreen_score below 70 = do not include
- Be conservative — 5 strong clusters > 10 weak ones"""

    lines = [
        f"# 📅 월간 패턴 분석 리포트 — {month}",
        f"> 분석: {now_str}",
        f"> 대상 주차: {', '.join(week_tags)}",
        f"> 총 {total_items}건 분석 | 지속 키워드 기준: {MIN_WEEKS}주/{len(weeks)}주 이상",
        "",
        "---",
        "",
        "## 핵심 인사이트",
        "",
        f"- 전체 {len(week_appearance)}개 키워드 중 {len(persistent)}개가 "
        f"{MIN_WEEKS}주 이상 지속 등장",
        f"- 이것이 진짜 에버그린 후보 — 한 주 반짝이 아닌 지속 수요",
        "",
        "---",
        "",
        "## ✂️ AI 월간 분석 프롬프트 (전체 복사 → AI 웹에 붙여넣기)",
        "",
        "```",
        prompt_block,
        "```",
        "",
        "---",
        "",
        "## 지속 패턴 키워드 상세",
        "",
        f"### 단어 ({MIN_WEEKS}주+ 등장, 상위 40개)",
        "",
        "| 키워드 | 총 횟수 | 등장 주수 |",
        "|---|---|---|",
    ]
    for w, c in persistent_words:
        lines.append(f"| {w} | {c}회 | {week_appearance[w]}주 |")

    lines += [
        "",
        f"### 2단어 조합 ({MIN_WEEKS}주+ 등장, 상위 20개)",
        "",
        "| 조합 | 총 횟수 | 등장 주수 |",
        "|---|---|---|",
    ]
    for w, c in persistent_bigrams:
        lines.append(f"| {w} | {c}회 | {week_appearance[w]}주 |")

    lines += [
        "",
        "---",
        "",
        "## 단발성 주제 (참고 — 1~2주만 등장)",
        "",
        "| 키워드 | 총 횟수 |",
        "|---|---|",
    ]
    for w, c in sorted(occasional.items(), key=lambda x: -x[1])[:20]:
        lines.append(f"| {w} | {c}회 |")

    lines += [
        "",
        "---",
        "",
        "## [D] AI 분석 결과 입력란",
        "",
        "| # | 클러스터명 | 유형 | 제안 제목 | 에버그린 | 어필리에이트 | 시리즈? | timing |",
        "|---|---|---|---|---|---|---|---|",
        "| 1 | | | | | | | |",
        "| 2 | | | | | | | |",
        "| 3 | | | | | | | |",
        "",
        "**최종 선택:**",
        "",
        "**Trends 확인 결과:**",
        "",
    ]

    return "\n".join(lines), month


if __name__ == "__main__":
    print("=" * 60)
    print("📅 월간 패턴 분석 (AI 호출 없음)")
    print("=" * 60 + "\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 주간 로그 로드
    print(f"📂 최근 {WEEKS_TO_USE}주치 로그 로드 중...")
    weeks = load_weekly_logs()

    if len(weeks) < 2:
        print(f"\n⚠️ 주간 로그가 {len(weeks)}개뿐이에요.")
        print(f"   월간 분석은 최소 2개, 정확한 분석은 {WEEKS_TO_USE}개가 필요해요.")
        print(f"   지금은 주간 스캔을 계속 쌓아주세요.")
        raise SystemExit(0)

    if len(weeks) < WEEKS_TO_USE:
        print(f"\n⚠️ {WEEKS_TO_USE}주치 중 {len(weeks)}주치만 있음 — 부분 분석으로 진행")
        # MIN_WEEKS도 비례 조정
        adj_min = max(1, int(MIN_WEEKS * len(weeks) / WEEKS_TO_USE))
        print(f"   최소 등장 기준: {MIN_WEEKS}주 → {adj_min}주로 조정")
        CFG["monthly"]["min_weeks_to_qualify"] = adj_min
        MIN_WEEKS = adj_min

    print(f"\n🔍 패턴 분석 중...")
    total, week_appearance, persistent, occasional = analyze_patterns(weeks)

    print(f"  • 지속 키워드({MIN_WEEKS}주+): {len(persistent)}개")
    print(f"  • 단발성 키워드: {len(occasional)}개")

    report, month = build_monthly_report(
        weeks, total, week_appearance, persistent, occasional
    )

    report_path = os.path.join(OUTPUT_DIR, f"monthly_report_{month}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 월간 리포트: {report_path}")
    print(f"\n🏁 완료!")
    print(f"\n다음 단계:")
    print(f"  1. {report_path} 열기")
    print(f"  2. [✂️ AI 월간 분석 프롬프트] 복사 → AI 웹에 붙여넣기")
    print(f"  3. 결과 확인 → 장기 콘텐츠 시리즈 기획")
