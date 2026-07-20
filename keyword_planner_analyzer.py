# =====================================================================
# 🔑 Keyword Planner CSV 파서 (keyword_planner_analyzer.py)
# =====================================================================
# 목적: Google Ads Keyword Planner에서 내려받은 CSV를 파싱해서
#       {keyword, monthly_searches, competition, competition_index}
#       목록으로 변환. trends_analyzer.py가 import해서 사용.
#
# 지원 형식:
#   인코딩: UTF-16-LE(기본 KP 내보내기), UTF-16, UTF-8(-sig)
#   구분자: 탭 / 콤마 자동 감지
#   헤더:   영문(Keyword / Avg. monthly searches / Competition /
#           Competition (indexed value)) + 한국어(키워드 / 월평균 검색량 /
#           경쟁 / 경쟁(색인값)) 둘 다 지원
#   메타데이터 줄(리포트 제목/기간)은 자동 스킵
# =====================================================================

import re
import csv
import io

# 경쟁도 값 정규화
_COMPETITION_MAP = {
    "low": "LOW", "낮음": "LOW",
    "medium": "MEDIUM", "중간": "MEDIUM",
    "high": "HIGH", "높음": "HIGH",
}

# 헤더 후보 (소문자 비교)
_KEYWORD_COLS  = ["keyword", "키워드"]
_SEARCHES_COLS = ["avg. monthly searches", "monthly searches", "월평균 검색량", "평균 월간 검색량"]
_COMP_COLS     = ["competition", "경쟁", "경쟁도"]
_COMP_IDX_COLS = ["competition (indexed value)", "경쟁(색인값)", "경쟁 (색인값)", "competition indexed value"]


def _read_text(filepath):
    """인코딩 자동 감지해서 텍스트 반환."""
    raw = open(filepath, "rb").read()
    for enc in ("utf-16", "utf-16-le", "utf-8-sig", "utf-8", "cp949"):
        try:
            text = raw.decode(enc)
            # 디코딩 성공 + 널문자 없음 = 정상
            if "\x00" not in text:
                return text
        except (UnicodeDecodeError, UnicodeError):
            continue
    # 최후: 널문자 제거하고 utf-8 강제
    return raw.decode("utf-8", errors="replace").replace("\x00", "")


def _parse_searches(value):
    """검색량 값 정규화. '50,000' / '1K – 10K' / '1천~1만' → 대표 숫자."""
    if value is None:
        return 0
    s = str(value).strip().replace(",", "").replace('"', "")
    if not s or s == "-":
        return 0
    # 순수 숫자
    if re.fullmatch(r"\d+", s):
        return int(s)
    # 범위형: "1K – 10K", "1천~1만" 등 → 상한 사용 (보수적 추정은 하한이지만
    # KP 범위는 대략적이므로 중간값 대신 상한의 절반을 대표값으로)
    s_norm = (s.replace("천", "K").replace("만", "0K")  # 1만 → 10K
               .replace("–", "-").replace("~", "-"))
    nums = re.findall(r"(\d+(?:\.\d+)?)\s*([KkMm]?)", s_norm)
    vals = []
    for num, unit in nums:
        v = float(num)
        if unit.lower() == "k":
            v *= 1_000
        elif unit.lower() == "m":
            v *= 1_000_000
        vals.append(int(v))
    if not vals:
        return 0
    if len(vals) >= 2:
        return (vals[0] + vals[1]) // 2  # 범위 중간값
    return vals[0]


def _find_col(header_lower, candidates):
    for i, col in enumerate(header_lower):
        for cand in candidates:
            if cand in col:
                return i
    return None


def parse_kp_csv(filepath):
    """
    KP CSV 파싱 → {"keywords": [...], "error": None or str}
    keywords 항목: {keyword, monthly_searches, competition, competition_index}
    """
    try:
        text = _read_text(filepath)
    except OSError as e:
        return {"keywords": [], "error": f"파일 읽기 실패: {e}"}

    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return {"keywords": [], "error": "빈 파일"}

    # 구분자 감지: 헤더 줄 후보에서 탭/콤마 개수 비교
    # 헤더 줄 = 키워드 컬럼명이 포함된 첫 줄 (메타데이터 줄 스킵)
    header_idx = None
    for i, ln in enumerate(lines[:10]):
        low = ln.lower()
        if any(k in low for k in _KEYWORD_COLS) and (
           any(k in low for k in [c.lower() for c in _SEARCHES_COLS]) or "search" in low or "검색" in low):
            header_idx = i
            break
    if header_idx is None:
        return {"keywords": [], "error": "헤더 행을 찾을 수 없음 (Keyword/검색량 컬럼 필요)"}

    header_line = lines[header_idx]
    delimiter = "\t" if header_line.count("\t") >= header_line.count(",") else ","

    reader = csv.reader(io.StringIO("\n".join(lines[header_idx:])), delimiter=delimiter)
    rows = list(reader)
    header = [h.strip().lower() for h in rows[0]]

    kw_i   = _find_col(header, _KEYWORD_COLS)
    sr_i   = _find_col(header, [c.lower() for c in _SEARCHES_COLS])
    comp_i = _find_col(header, [c.lower() for c in _COMP_COLS])
    idx_i  = _find_col(header, [c.lower() for c in _COMP_IDX_COLS])

    if kw_i is None:
        return {"keywords": [], "error": "Keyword 컬럼 없음"}

    keywords = []
    for row in rows[1:]:
        if len(row) <= kw_i:
            continue
        kw = row[kw_i].strip()
        if not kw:
            continue
        searches = _parse_searches(row[sr_i]) if sr_i is not None and len(row) > sr_i else 0
        comp_raw = row[comp_i].strip().lower() if comp_i is not None and len(row) > comp_i else ""
        comp     = _COMPETITION_MAP.get(comp_raw, comp_raw.upper() or "UNKNOWN")
        comp_idx = 0
        if idx_i is not None and len(row) > idx_i:
            m = re.search(r"\d+", row[idx_i])
            comp_idx = int(m.group()) if m else 0
        keywords.append({
            "keyword":           kw,
            "monthly_searches":  searches,
            "competition":       comp,
            "competition_index": comp_idx,
        })

    if not keywords:
        return {"keywords": [], "error": "파싱된 키워드 0개"}
    return {"keywords": keywords, "error": None}


# =====================================================================
# 클러스터 매칭
# =====================================================================

_STOPWORDS = {"the", "a", "an", "to", "for", "of", "in", "on", "and", "or",
              "how", "is", "vs", "with", "your", "what", "are"}


def _tokens(text):
    """토큰화 + 단복수 정규화 (extensions ↔ extension 매칭)."""
    out = set()
    for t in re.findall(r"[a-z0-9]+", str(text).lower()):
        if len(t) <= 1 or t in _STOPWORDS:
            continue
        # 단순 복수형 제거: 4자 이상 + s로 끝나면 s 제거형도 비교 대상
        if len(t) > 3 and t.endswith("s"):
            t = t[:-1]
        out.add(t)
    return out


def match_keywords_to_cluster(kp_keywords, cluster_info):
    """
    KP 키워드 목록에서 이 클러스터에 해당하는 것만 골라 반환.
    매칭 기준: hub_keyword 토큰이 전부 포함 OR
              클러스터 키워드 풀과 2개 이상 토큰 겹침.
    """
    pool = _tokens(cluster_info.get("hub_keyword", ""))
    pool |= _tokens(cluster_info.get("cluster_name", ""))
    for kw in cluster_info.get("spoke_keywords", []) or []:
        pool |= _tokens(kw)
    for kw in cluster_info.get("trends_queries", []) or []:
        pool |= _tokens(kw)

    hub_tokens = _tokens(cluster_info.get("hub_keyword", ""))

    matched = []
    for item in kp_keywords:
        kw_tokens = _tokens(item["keyword"])
        if not kw_tokens:
            continue
        hub_hit     = hub_tokens and hub_tokens.issubset(kw_tokens)
        overlap_hit = len(kw_tokens & pool) >= 2
        if hub_hit or overlap_hit:
            matched.append(item)

    # 정렬: hub_keyword 포함 여부 우선 → 검색량 순
    def _match_score(item):
        kw_tokens = _tokens(item["keyword"])
        hub_exact = hub_tokens and hub_tokens.issubset(kw_tokens)
        return (0 if hub_exact else 1, -item["monthly_searches"])

    matched.sort(key=_match_score)
    return matched


if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 2:
        print("사용법: python keyword_planner_analyzer.py <kp_csv_path>")
        sys.exit(1)
    result = parse_kp_csv(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
