# =====================================================================
# 📈 Trends + Keyword Planner 통합 분석기 (trends_analyzer.py) — v2
# =====================================================================
# 목적: 주차별 trends 폴더의 CSV를 자동 감지/분석해서
#       Grade(A/B/C) 판정 + content_pipeline.json 업데이트
#
# 폴더 구조 (선택 기록 시 pipeline.py가 자동 생성):
#   research_data/trends/YYYY-WW/
#     ├── 01-{cluster-slug}/          ← Trends CSV 3종 세트를 여기에
#     │     time_series_*.csv         (컬럼: Time, {키워드})
#     │     searched_with_top-*.csv   (컬럼: query, search interest, ...)
#     │     searched_with_rising-*.csv
#     ├── 02-{cluster-slug}/
#     ├── keyword_planner_*.csv 또는 Keyword_Stats_*.csv  ← 주차 루트에 1개
#     └── analysis_result.json        ← 이 스크립트가 생성 (덮어씀)
#
# Grade:
#   A = Trends + KP 둘 다 매칭 → 자동 발행 큐
#   B = 둘 중 하나만          → 발행 (부분 검증 표시)
#   C = 둘 다 없음            → 발행 보류 (수동 오버라이드 가능)
#
# 사용:
#   python trends_analyzer.py            ← 이번 주 분석
#   python trends_analyzer.py 2026-W28   ← 특정 주 분석
#   (앱에서는 analyze_week() 함수를 직접 import)
# =====================================================================

import os
import re
import sys
import csv
import glob
import json
import statistics
from datetime import datetime, timezone

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from keyword_planner_analyzer import parse_kp_csv, match_keywords_to_cluster

TRENDS_ROOT   = os.path.join("research_data", "trends")
PIPELINE_FILE = "content_pipeline.json"

# 패턴 판정 임계값
RISING_RATIO    = 1.15   # 최근 8주 평균 / 전체 평균 ≥ 1.15 → RISING
DECLINING_RATIO = 0.85   # ≤ 0.85 → DECLINING
SPIKE_PEAK_RATIO = 2.5   # 피크 / 현재 ≥ 2.5 (하락 중일 때) → SPIKE


# =====================================================================
# 공용 유틸 (write.py와 동일한 slugify — 폴더명 매칭 일관성)
# =====================================================================

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def get_week_tag():
    return datetime.now(timezone.utc).strftime("%Y-W%W")


def load_pipeline():
    try:
        with open(PIPELINE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"covered_clusters": {}, "weekly_selections": {}, "published": []}


def save_pipeline(data):
    data["_last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(PIPELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =====================================================================
# Trends CSV 파싱
# =====================================================================

def _read_lines(filepath):
    for enc in ("utf-8-sig", "utf-8", "utf-16", "cp949"):
        try:
            with open(filepath, encoding=enc) as f:
                text = f.read()
            if "\x00" not in text:
                return text.splitlines()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return []


def parse_time_series(filepath):
    """time_series CSV → (keyword, [values]) — 헤더 위치 유연 탐색."""
    lines = [ln for ln in _read_lines(filepath) if ln.strip()]
    header_idx = None
    for i, ln in enumerate(lines[:5]):
        low = ln.lower()
        if low.startswith(("time", "week", "day", "주", "날짜")):
            header_idx = i
            break
    if header_idx is None:
        return None, []

    reader = list(csv.reader(lines[header_idx:]))
    header = reader[0]
    if len(header) < 2:
        return None, []
    # 키워드명: 두 번째 컬럼. ": (United States)" 같은 지역 접미어 제거
    keyword = re.sub(r":\s*\(.*\)\s*$", "", header[1]).strip()

    values = []
    for row in reader[1:]:
        if len(row) < 2:
            continue
        raw = row[1].strip()
        if raw in ("<1", "＜1"):
            values.append(0)
        else:
            m = re.search(r"\d+", raw)
            if m:
                values.append(int(m.group()))
    return keyword, values


def parse_query_csv(filepath):
    """top/rising/relatedEntities CSV → [{query, interest}] (상위 10개)."""
    lines = [ln for ln in _read_lines(filepath) if ln.strip()]
    header_idx = None
    for i, ln in enumerate(lines[:8]):
        low = ln.lower()
        if any(k in low for k in ["query", "검색어", "topic", "entity", "value"]):
            header_idx = i
            break
    if header_idx is None:
        return []
    reader = list(csv.reader(lines[header_idx:]))
    out = []
    for row in reader[1:11]:
        if row and row[0].strip():
            out.append({
                "query":    row[0].strip(),
                "interest": row[1].strip() if len(row) > 1 else "",
            })
    return out


def judge_pattern(values):
    """시계열 → RISING / STABLE / DECLINING / SPIKE / UNKNOWN"""
    if not values or len(values) < 8:
        return "UNKNOWN", {}
    avg_all    = statistics.mean(values)
    if avg_all == 0:
        return "UNKNOWN", {}
    recent     = values[-8:]
    avg_recent = statistics.mean(recent)
    current    = statistics.mean(values[-2:])
    peak       = max(values)
    ratio      = avg_recent / avg_all

    stats = {
        "avg_all":    round(avg_all, 1),
        "avg_recent8": round(avg_recent, 1),
        "current":    round(current, 1),
        "peak":       peak,
        "recent_ratio": round(ratio, 2),
    }

    if ratio >= RISING_RATIO:
        return "RISING", stats
    if ratio <= DECLINING_RATIO:
        if current > 0 and peak / max(current, 1) >= SPIKE_PEAK_RATIO:
            return "SPIKE", stats     # 피크 찍고 급락 = 스파이크성
        return "DECLINING", stats
    return "STABLE", stats            # 평탄 유지 = 에버그린


# =====================================================================
# 주차 폴더 스캔 + 분석
# =====================================================================

def get_week_dir(week_tag):
    return os.path.join(TRENDS_ROOT, week_tag)


def scan_week_folder(week_tag):
    """주차 폴더 스캔 → {cluster_folders: {slug: {path, csvs}}, kp_files: []}"""
    week_dir = get_week_dir(week_tag)
    result = {"week_dir": week_dir, "exists": os.path.isdir(week_dir),
              "cluster_folders": {}, "kp_files": []}
    if not result["exists"]:
        return result

    for entry in sorted(os.listdir(week_dir)):
        full = os.path.join(week_dir, entry)
        if os.path.isdir(full):
            # NN-slug → slug 추출
            slug = re.sub(r"^\d+-", "", entry)
            result["cluster_folders"][slug] = {
                "folder_name": entry,
                "path":        full,
                "time_series": sorted(
                    glob.glob(os.path.join(full, "time_series*.csv")) +
                    glob.glob(os.path.join(full, "multiTimeline*.csv"))
                    # geoMap은 지역별 데이터 — 시계열 아님, 제외
                ),
                "top":         sorted(
                    glob.glob(os.path.join(full, "*top-search*.csv")) +
                    glob.glob(os.path.join(full, "*top_search*.csv")) +
                    glob.glob(os.path.join(full, "relatedEntities*.csv"))
                ),
                "rising":      sorted(
                    glob.glob(os.path.join(full, "*rising*.csv")) +
                    glob.glob(os.path.join(full, "relatedQueries*.csv")) +
                    glob.glob(os.path.join(full, "relatedEntities*.csv"))
                ),
            }
        elif entry.lower().endswith(".csv"):
            low = entry.lower()
            if "keyword" in low or "kp_" in low:
                result["kp_files"].append(full)
    return result


def analyze_week(week_tag=None, update_pipeline=True):
    """
    주차 폴더 전체 분석 → Grade 판정 → pipeline 업데이트.
    반환: 리포트 dict (앱에서 표시용)
    """
    if not week_tag:
        week_tag = get_week_tag()

    scan = scan_week_folder(week_tag)
    report = {
        "week_tag":   week_tag,
        "week_dir":   scan["week_dir"],
        "clusters":   [],
        "kp_parsed":  0,
        "kp_error":   None,
        "unassigned_keywords": [],
        "updated":    False,
    }

    if not scan["exists"]:
        report["kp_error"] = f"주차 폴더 없음: {scan['week_dir']} (기획안 선택 기록 시 자동 생성됨)"
        return report

    # KP CSV 파싱 (주차 루트, 가장 최신 파일)
    kp_keywords = []
    if scan["kp_files"]:
        kp_result = parse_kp_csv(scan["kp_files"][-1])
        kp_keywords = kp_result["keywords"]
        report["kp_parsed"] = len(kp_keywords)
        report["kp_error"]  = kp_result["error"]

    # 파이프라인에서 이번 주 선택 기획안 로드
    data       = load_pipeline()
    selections = data.get("weekly_selections", {}).get(week_tag, [])
    assigned_kw_set = set()

    # parent_hub 기준으로 중복 분석 방지
    # 같은 허브의 스포크 여러 개가 있어도 Trends/KP 분석은 1번만
    analyzed_hubs = {}  # parent_hub → entry (결과 재사용)

    for sel in selections:
        cluster_name = sel.get("cluster_name", "")
        parent_hub   = sel.get("parent_hub", "")
        slug         = slugify(cluster_name)
        folder       = scan["cluster_folders"].get(slug)

        # 같은 parent_hub면 이전 분석 결과 재사용 (Trends/KP는 허브 기준)
        if parent_hub and parent_hub in analyzed_hubs:
            prev = analyzed_hubs[parent_hub]
            # pipeline 반영만 별도로 (cluster_name은 다름)
            if update_pipeline:
                sel["trends_pattern"]    = prev["trends_pattern"]
                sel["trends_keyword"]    = prev["trends_keyword"]
                sel["verified_keywords"] = prev["verified_keywords"]
                sel["data_grade"]        = prev["grade"]
                if prev.get("rising_queries"):
                    sel["trends_opportunities"] = [
                        q["query"] for q in prev["rising_queries"][:5]]
            continue  # 중복 표시 스킵

        entry = {
            "cluster_name":   cluster_name,
            "slug":           slug,
            "folder":         folder["folder_name"] if folder else None,
            "trends_pattern": "UNKNOWN",
            "trends_stats":   {},
            "trends_keyword": "",
            "rising_queries": [],
            "verified_keywords": [],
            "grade":          "C",
            "warnings":       [],
        }

        # --- Trends 분석 ---
        has_trends = False
        if folder and folder["time_series"]:
            ts_path = folder["time_series"][-1]  # 최신 파일
            keyword, values = parse_time_series(ts_path)
            if values:
                pattern, stats = judge_pattern(values)
                entry["trends_pattern"] = pattern
                entry["trends_stats"]   = stats
                entry["trends_keyword"] = keyword or ""
                has_trends = pattern != "UNKNOWN"
                # 키워드 검증: 폴더에 잘못된 CSV가 들어갔는지 확인
                if keyword:
                    kw_tokens  = set(re.findall(r"[a-z0-9]+", keyword.lower()))
                    hub_tokens = set(re.findall(r"[a-z0-9]+",
                                     str(sel.get("hub_keyword", "")).lower()))
                    if hub_tokens and not (kw_tokens & hub_tokens):
                        entry["warnings"].append(
                            f"time_series 키워드 '{keyword}'가 hub '{sel.get('hub_keyword')}'와 "
                            f"무관해 보임 — CSV를 잘못된 폴더에 넣었는지 확인")
            else:
                entry["warnings"].append("time_series CSV 파싱 실패")

        if folder and folder["rising"]:
            entry["rising_queries"] = parse_query_csv(folder["rising"][-1])

        # --- KP 매칭 ---
        has_kp = False
        if kp_keywords:
            matched = match_keywords_to_cluster(kp_keywords, sel)
            if matched:
                # 롱테일 품질 필터: LOW/MEDIUM 경쟁 + 월 100 이상
                quality = [v for v in matched
                           if v.get("monthly_searches", 0) >= 100
                           and v.get("competition", "HIGH") in ("LOW", "MEDIUM", "?")]

                # 정렬 전략:
                #   1) LOW 경쟁 우선
                #   2) 단어 수 많은 것 우선 (롱테일)
                #   3) 검색량 높은 것
                def sort_key(v):
                    comp_score = {"LOW": 0, "MEDIUM": 1, "?": 2, "HIGH": 3}.get(
                        v.get("competition", "HIGH"), 3)
                    word_count = len(v["keyword"].split())
                    longtail_bonus = 0 if word_count >= 3 else 1  # 3단어 이상 우선
                    return (comp_score, longtail_bonus, -v.get("monthly_searches", 0))

                quality.sort(key=sort_key)

                # 상위 8개 저장 (롱테일 우선 정렬됨)
                entry["verified_keywords"] = quality[:8] if quality else matched[:8]
                assigned_kw_set.update(m["keyword"] for m in matched)

                top_searches = quality[0]["monthly_searches"] if quality else 0
                if top_searches >= 100:
                    has_kp = True
                else:
                    entry["warnings"].append(
                        f"KP 품질 기준 키워드 없음 "
                        f"(LOW/MEDIUM + 월100이상 조건 미충족)")

        # --- Grade ---
        grade_reasons = []

        if has_trends:
            stats = entry["trends_stats"]
            grade_reasons.append(
                f"Trends ✅ {entry['trends_pattern']} "
                f"(최근8주 {stats.get('avg_recent8',0):.0f} / "
                f"전체평균 {stats.get('avg_all',0):.0f} / "
                f"비율 {stats.get('recent_ratio',0):.2f})"
            )
        else:
            grade_reasons.append("Trends ❌ 시계열 데이터 없음 또는 UNKNOWN")

        if has_kp:
            vk = entry["verified_keywords"]
            top = vk[0]
            longtail_count = sum(1 for v in vk if len(v["keyword"].split()) >= 3)
            low_count = sum(1 for v in vk if v.get("competition") == "LOW")
            grade_reasons.append(
                f"KP ✅ 매칭 {len(vk)}개 | "
                f"롱테일(3단어+) {longtail_count}개 | "
                f"LOW경쟁 {low_count}개 | "
                f"최대: '{top['keyword']}' 월 {top['monthly_searches']:,}"
            )
        elif entry["verified_keywords"]:
            top = entry["verified_keywords"][0]
            grade_reasons.append(
                f"KP ⚠️ 매칭됐으나 품질 미달 "
                f"(최대 {top['monthly_searches']:,}/월 또는 HIGH경쟁)"
            )
        else:
            grade_reasons.append("KP ❌ 클러스터 관련 키워드 없음")

        if has_trends and has_kp:
            entry["grade"] = "A"
            grade_reasons.append("→ Grade A: Trends 타이밍 + KP 롱테일 모두 검증됨")
        elif has_trends or has_kp:
            entry["grade"] = "B"
            grade_reasons.append("→ Grade B: 부분 검증 — 발행 가능하나 키워드 최적화 미완")
        else:
            entry["grade"] = "C"
            grade_reasons.append("→ Grade C: 검증 데이터 없음 — 발행 보류 권장")

        entry["grade_reasons"] = grade_reasons

        report["clusters"].append(entry)

        # analyzed_hubs에 저장 (같은 허브의 다른 스포크는 재사용)
        if parent_hub:
            analyzed_hubs[parent_hub] = entry

        # --- pipeline 반영 ---
        if update_pipeline:
            sel["trends_pattern"]    = entry["trends_pattern"]
            sel["trends_keyword"]    = entry["trends_keyword"]
            sel["verified_keywords"] = entry["verified_keywords"]
            sel["data_grade"]        = entry["grade"]
            if entry["rising_queries"]:
                sel["trends_opportunities"] = [q["query"] for q in entry["rising_queries"][:5]]
            # covered_clusters에도 패턴 반영
            cc = data.get("covered_clusters", {}).get(cluster_name)
            if cc:
                cc["trends_pattern"] = entry["trends_pattern"]

    # 미배정 KP 키워드
    report["unassigned_keywords"] = [
        k["keyword"] for k in kp_keywords if k["keyword"] not in assigned_kw_set][:15]

    if update_pipeline and selections:
        save_pipeline(data)
        report["updated"] = True

    # 분석 결과 저장 (재실행 시 덮어씀)
    result_path = os.path.join(scan["week_dir"], "analysis_result.json")
    try:
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    except OSError:
        pass

    return report


# =====================================================================
# CLI
# =====================================================================

def print_report(report):
    print(f"\n{'='*60}")
    print(f"📈 Trends + KP 분석 결과 — {report['week_tag']}")
    print(f"{'='*60}")
    if report.get("kp_error") and not report["clusters"]:
        print(f"⚠️  {report['kp_error']}")
        return
    print(f"KP 키워드 파싱: {report['kp_parsed']}개"
          + (f" (⚠️ {report['kp_error']})" if report["kp_error"] else ""))

    grade_icon = {"A": "🟢", "B": "🟡", "C": "🔴"}
    for c in report["clusters"]:
        icon = grade_icon.get(c["grade"], "⬜")
        print(f"\n{icon} Grade {c['grade']} — {c['cluster_name']}")
        print(f"   폴더: {c['folder'] or '❌ 없음'}")
        for reason in c.get("grade_reasons", []):
            print(f"   {reason}")
        if c["verified_keywords"]:
            print(f"   검증 키워드 TOP 3:")
            for v in c["verified_keywords"][:3]:
                print(f"     · {v['keyword']} | 월 {v['monthly_searches']:,} | {v.get('competition','?')}")
        if c.get("rising_queries"):
            print(f"   급상승 검색어: {', '.join(q['query'] for q in c['rising_queries'][:3])}")
        for w in c["warnings"]:
            print(f"   ⚠️  {w}")
    if report["unassigned_keywords"]:
        print(f"\n📎 미배정 KP 키워드: {', '.join(report['unassigned_keywords'][:8])}")
    print()


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else None
    print_report(analyze_week(tag))
