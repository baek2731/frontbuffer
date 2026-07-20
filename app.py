# =====================================================================
# 🎛️ Frontbuffer 파이프라인 조수 (app.py) — v2 터미널 프리
# =====================================================================
# 목적: 터미널 의존 제거. 브라우저에서 전체 파이프라인 조작.
#       터미널은 최초 `streamlit run app.py` 한 번만 필요.
#
# 담당 범위:
#   [기획] ai_result 붙여넣기 저장 + 번호 선택으로 기획안 기록
#   [글쓰기] prep 버튼 실행 + 프롬프트 표시 + 초안 저장
#   [검증] review 버튼 실행 + 프롬프트 표시 + 최종본 저장
#   [발행] done 폼 입력 → 기록
#   [현황] 전체 진행 상황
#
# 설계 원칙: 로직은 write.py/pipeline.py에 있고 여긴 호출만.
#
# 실행: streamlit run app.py
# =====================================================================

import os
import io
import re
import json
import contextlib
from pathlib import Path

import streamlit as st

# posts_manager 선택적 import
try:
    from posts_manager import (load_posts, save_posts, update_live_url,
                                resolve_internal_links, get_hub_summary,
                                get_unresolved_links)
    _PM_OK = True
except ImportError:
    _PM_OK = False

from write import (
    slugify, load_pipeline, cmd_prep, cmd_review, record_publish,
    get_week_tag, check_draft_quality, discard_cluster,
    PROMPTS_DIR, DRAFTS_DIR, FINAL_DIR, OUTPUT_DIR,
)
from pipeline import record_selections

st.set_page_config(page_title="Frontbuffer 파이프라인", page_icon="✍️", layout="wide")

AI_RESULT_PATH = os.path.join(OUTPUT_DIR, "ai_result_latest.json")


# =====================================================================
# 유틸
# =====================================================================

def clean_markdown_escapes(text):
    r"""이스케이프된 마크다운 문법 복원 (\# → #)."""
    return re.sub(r"\\([#*\-\[\]`>_])", r"\1", text)


def extract_markdown_block(text):
    """```markdown ... ``` 코드블록이 있으면 내부만 추출."""
    match = re.search(r"```(?:markdown|md)?\s*\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def extract_json_block(text):
    """붙여넣은 텍스트에서 JSON 추출 (코드블록 or 원본)."""
    match = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    raw = match.group(1) if match else text
    return json.loads(raw.strip())


def run_captured(fn, *args, **kwargs):
    """CLI 함수 실행하며 stdout 캡처 → (성공여부, 로그)."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            fn(*args, **kwargs)
        return True, buf.getvalue()
    except SystemExit:
        return False, buf.getvalue()
    except Exception as e:
        return False, buf.getvalue() + f"\n❌ 오류: {e}"


def get_candidates(exclude_done=False, min_stage=None, max_stage=None):
    """
    exclude_done=True: stage>=5 제외 (글쓰기 탭)
    min_stage=N:       stage>=N 항목만 (검증 탭: min_stage=2)
    max_stage=N:       stage<=N 항목만 (발행 탭: max_stage=4 — published 제외)
    """
    data   = load_pipeline()
    result = []
    for week, sels in sorted(data.get("weekly_selections", {}).items(), reverse=True):
        for s in sels:
            if s.get("status") == "candidate":
                slug = slugify(s["cluster_name"])
                ct   = s.get("content_type", "")
                stage_num, _ = get_stage(slug, ct)
                if exclude_done and stage_num >= 5:
                    continue
                if min_stage is not None and stage_num < min_stage:
                    continue
                if max_stage is not None and stage_num > max_stage:
                    continue
                result.append({
                    "week": week,
                    "cluster": s["cluster_name"],
                    "type": ct or "?",
                    "timing": s.get("timing", "?"),
                    "competition": s.get("competition_level", "?"),
                    "title": s.get("suggested_title", ""),
                })
    return result


def get_stage(slug, content_type=""):
    """content_type별로 다른 파일을 참조해 단계 판단."""
    ct = content_type.upper().strip() if content_type else ""
    ct_fname = f"{slug}_{ct}.md" if ct else f"{slug}.md"
    ct_review = (f"review_prompt_{slug}_{ct}.txt" if ct
                 else f"review_prompt_{slug}.txt")
    ct_prompt = (f"write_prompt_{slug}_{ct}_*.txt" if ct
                 else f"write_prompt_{slug}_*.txt")

    write_prompts = list(Path(PROMPTS_DIR).glob(ct_prompt))         if os.path.exists(PROMPTS_DIR) else []
    draft  = Path(DRAFTS_DIR) / ct_fname
    review = Path(PROMPTS_DIR) / ct_review
    final  = Path(FINAL_DIR) / ct_fname

    if final.exists():
        return 5, "✅ 최종본 완료 — [발행] 탭에서 기록"
    if review.exists():
        return 4, "🟡 review 프롬프트 준비됨 → Claude에 붙여넣고 최종본 저장"
    if draft.exists():
        return 3, "🟡 초안 저장됨 → [검증] 탭에서 review 실행"
    if write_prompts:
        return 2, "🟡 글쓰기 프롬프트 준비됨 → Gemini에 붙여넣고 초안 저장"
    return 1, "⬜ 시작 전 → [글쓰기] 탭에서 prep 실행"


import subprocess
import sys

# =====================================================================
# UI
# =====================================================================

st.title("✍️ Frontbuffer Editorial 글 생성 파이프라인")

# =====================================================================
# 소재 큐 잔여량 체크 — 앱 전체에서 항상 표시
# =====================================================================
def _check_queue_status():
    """
    Grade A/B 후보 중 아직 미완료(stage < 5)인 항목 수 반환.
    config.json의 low_queue_threshold(기본 3)와 비교해 알림 여부 결정.
    """
    try:
        cfg_path = Path("config.json")
        threshold = 3
        if cfg_path.exists():
            import json as _json
            _cfg = _json.loads(cfg_path.read_text(encoding="utf-8"))
            threshold = _cfg.get("collect", {}).get("low_queue_threshold", 3)
    except Exception:
        threshold = 3

    data = load_pipeline()
    ab_count = 0
    for week, sels in data.get("weekly_selections", {}).items():
        for s in sels:
            if s.get("status") != "candidate":
                continue
            grade = s.get("data_grade", "")
            if grade not in ("A", "B"):
                continue
            slug    = slugify(s["cluster_name"])
            ct      = s.get("content_type", "")
            stage_n, _ = get_stage(slug, ct)
            if stage_n < 5:  # 미완료
                ab_count += 1
    return ab_count, threshold

_queue_count, _queue_threshold = _check_queue_status()

if _queue_count == 0:
    st.error(
        f"🚨 **소재 큐 비어있음** — Grade A/B 미완료 클러스터가 없어요.  \n"
        f"리서치 탭에서 리서치를 실행하고 Trends CSV를 추가해주세요.",
        icon="🚨"
    )
elif _queue_count < _queue_threshold:
    st.warning(
        f"⚠️ **소재 부족 임박** — Grade A/B 미완료 클러스터 {_queue_count}개 남음 "
        f"(기준: {_queue_threshold}개 미만).  \n"
        f"리서치 탭에서 리서치를 실행하고 Trends CSV를 추가해주세요.",
        icon="⚠️"
    )
# 정상 상태는 배너 없음 (화면 낭비 방지)

tab_research, tab_plan, tab_write, tab_review, tab_publish, tab_status = st.tabs(
    ["🔍 리서치", "📋 기획", "1️⃣ 글쓰기 (Gemini)", "2️⃣ 검증+수정 (Claude)", "3️⃣ 발행 기록", "📊 현황"])

# =====================================================================
# 탭: 리서치
# =====================================================================
with tab_research:
    st.markdown("#### 🔍 주간 리서치 실행")
    st.caption("매주 월요일 1회 실행. 뉴스 RSS 수집 → AI 분석 프롬프트 생성.")

    week_tag     = get_week_tag()
    # 새 구조: weekly/{week_tag}/raw_research_log.json
    weekly_dir   = Path(OUTPUT_DIR) / "weekly" / week_tag
    raw_log_path = weekly_dir / "raw_research_log.json"
    prompt_path  = weekly_dir / "prompt.txt"
    # 구버전 fallback (루트)
    if not raw_log_path.exists():
        raw_log_path = Path(OUTPUT_DIR) / f"raw_research_log_{week_tag}.json"
    if not prompt_path.exists():
        prompt_path  = Path(OUTPUT_DIR) / f"prompt_{week_tag}.txt"

    # 이번 주 리서치 현황
    if raw_log_path.exists():
        import json as _json
        with open(raw_log_path, encoding="utf-8") as f:
            raw = _json.load(f)
        st.success(f"✅ 이번 주({week_tag}) 리서치 완료 — {raw.get('item_count', 0)}건 수집됨")
        already_done = True
    else:
        st.info(f"⬜ 이번 주({week_tag}) 리서치 아직 안 됨")
        already_done = False

    col_l, col_r = st.columns(2)

    with col_l:
        if already_done:
            st.warning("이번 주 리서치가 이미 있어요. 새 소스 추가 후 재실행하려면 아래 버튼을 누르세요.")
            run_label = "🔄 리서치 재실행 (덮어쓰기)"
        else:
            run_label = "🚀 리서치 실행"

        if st.button(run_label, type="primary"):
            with st.spinner("뉴스 RSS 수집 중... (2~5분 소요)"):
                result = subprocess.run(
                    [sys.executable, "-u", "research.py"],
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                    env={**os.environ, "PYTHONIOENCODING": "utf-8"}
                )
            if result.returncode == 0:
                st.success("✅ 리서치 완료!")
                st.code(result.stdout, language=None)
                st.rerun()
            else:
                st.error("❌ 리서치 실패")
                st.code(result.stderr or result.stdout, language=None)

    with col_r:
        st.markdown("#### 📤 Gemini에 넘길 프롬프트")
        if prompt_path.exists():
            with open(prompt_path, encoding="utf-8") as f:
                prompt_text = f.read()
            size_kb = len(prompt_text.encode())/1024
            st.caption(f"prompt_{week_tag}.txt ({size_kb:.1f} KB) — 우측 상단 복사 버튼")
            st.code(prompt_text, language=None)
        else:
            st.info("리서치 실행 후 프롬프트가 여기에 표시돼요.")

# =====================================================================
# 탭: 기획 — ai_result 저장 + 기획안 선택
# =====================================================================
with tab_plan:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### 📥 Gemini 주간 분석 결과 저장")
        st.caption("research.py의 prompt를 Gemini에 넣고 받은 JSON을 붙여넣으세요")
        ai_input = st.text_area("Gemini JSON 결과", height=250, key="ai_result_input")
        if st.button("💾 분석 결과 저장", type="primary"):
            if ai_input.strip():
                try:
                    parsed   = extract_json_block(ai_input)
                    week_tag = get_week_tag()
                    # 주차별 아카이브 (누적, 덮어쓰기 없음)
                    archive_path = os.path.join(OUTPUT_DIR, f"ai_result_{week_tag}.json")
                    with open(archive_path, "w", encoding="utf-8") as f:
                        json.dump(parsed, f, ensure_ascii=False, indent=2)
                    # latest 복사본 (trends_analyzer 등 기존 도구 호환용)
                    with open(AI_RESULT_PATH, "w", encoding="utf-8") as f:
                        json.dump(parsed, f, ensure_ascii=False, indent=2)
                    st.success(f"저장 완료: ai_result_{week_tag}.json (+ latest 갱신)")
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"JSON 형식 오류: {e}")
            else:
                st.error("내용이 비어있어요")

        if os.path.exists(AI_RESULT_PATH):
            st.success("✅ ai_result_latest.json 존재함")

    with col_r:
        st.markdown("#### ✅ 기획안 선택 (번호 클릭)")
        st.caption("Gemini 분석 결과에서 발행할 기획안을 체크하고 기록")

        if os.path.exists(AI_RESULT_PATH):
            try:
                with open(AI_RESULT_PATH, encoding="utf-8") as f:
                    ai_data = json.load(f)
                # ai_result 구조: 리스트 or {"clusters": [...]} 대응
                items = ai_data if isinstance(ai_data, list) else \
                        ai_data.get("clusters", ai_data.get("recommendations", []))

                if items:
                    # 기존 hub_clusters 목록 (parent_hub 선택용)
                    pl_now    = load_pipeline()
                    hubs_now  = list(pl_now.get("hub_clusters", {}).keys())

                    checked = []
                    for i, item in enumerate(items):
                        name  = item.get("cluster_name", f"항목 {i+1}")
                        ctype = item.get("content_type", "?")
                        tim   = item.get("timing", "?")
                        comp  = item.get("competition_level", "?")
                        veri  = item.get("verifiability", "?")
                        raw_hub = item.get("hub_keyword", "")
                        exp_type = item.get("expansion_type", "")
                        veri_icon = "✅" if veri == "HIGH" else "🟡" if veri == "MEDIUM" else "🔴"
                        exp_icon = " 📰" if exp_type == "NEWS" else " 🌿" if exp_type == "EVERGREEN" else ""
                        label = f"{name} ({ctype} | {tim} | 경쟁:{comp} | {veri_icon}{veri}{exp_icon})"
                        col_chk, col_hub = st.columns([3, 2])
                        with col_chk:
                            selected = st.checkbox(label, key=f"sel_{i}")
                        with col_hub:
                            # parent_hub 선택 (기존 허브에 귀속 or 새 허브 자동 생성)
                            hub_options = ["(자동 생성)"] + hubs_now
                            chosen_hub  = st.selectbox(
                                "귀속 허브", hub_options,
                                key=f"hub_{i}",
                                help="스포크가 속할 허브 클러스터. '자동 생성'은 hub_keyword로 허브를 새로 만들어요."
                            )
                        if selected:
                            if chosen_hub != "(자동 생성)":
                                item["parent_hub"] = chosen_hub
                            checked.append(item)

                    if st.button("📌 선택 기록", type="primary", disabled=not checked):
                        result = record_selections(checked)
                        if result["ok"]:
                            msg = f"{result['recorded']}개 기록 완료"
                            if result.get("skipped"):
                                msg += f" ({result['skipped']}개 중복 스킵)"
                            if result.get("trends_folders"):
                                msg += f" | Trends 폴더 {len(result['trends_folders'])}개 생성"
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(result.get("error", "기록 실패"))
                else:
                    st.warning("ai_result에서 기획안 목록을 찾지 못했어요")
            except Exception as e:
                st.error(f"ai_result 읽기 오류: {e}")
        else:
            st.info("먼저 왼쪽에서 Gemini 분석 결과를 저장하세요")

    # -----------------------------------------------------------------
    # Trends + Keyword Planner CSV 현황 및 분석 (기획 탭 하단)
    # -----------------------------------------------------------------
    st.divider()
    hd_col, btn_col1, btn_col2 = st.columns([3, 1, 1])
    with hd_col:
        st.markdown("#### 📈 Trends + Keyword Planner (Grade 검증)")
    with btn_col1:
        st.link_button("🔍 Google Trends",
                       "https://trends.google.com/trends/explore?geo=US&hl=en-US")
    with btn_col2:
        st.link_button("📊 Keyword Planner",
                       "https://ads.google.com/aw/keywordplanner/ideas/new")
    st.caption("선택 기록 후 아래 폴더가 자동 생성돼요. "
               "폴더 이름에 맞는 키워드로 Trends CSV 3종을 각 폴더에, "
               "KP CSV 1개를 주차 루트에 넣고 분석을 실행하세요.")

    from trends_analyzer import scan_week_folder, analyze_week

    scan     = scan_week_folder(week_tag)
    pl_data  = load_pipeline()
    week_sels = pl_data.get("weekly_selections", {}).get(week_tag, [])
    sel_by_slug = {slugify(s.get("cluster_name", "")): s for s in week_sels}

    if not scan["exists"] or not scan["cluster_folders"]:
        st.info(f"⬜ 이번 주 폴더 없음 — 위에서 선택 기록하면 "
                f"research_data/trends/{week_tag}/ 아래 클러스터 폴더가 자동 생성돼요.")
    else:
        st.caption(f"📂 {scan['week_dir']}")

        # hub_keyword 기준으로 Trends/KP 검색 힌트 표시
        import urllib.parse
        all_hub_keywords = []

        for slug_key, info in scan["cluster_folders"].items():
            sel = sel_by_slug.get(slug_key, {})
            ts = "✅" if info["time_series"] else "⬜"
            tp = "✅" if info["top"] else "⬜"
            rs = "✅" if info["rising"] else "⬜"
            grade = sel.get("data_grade", "")
            grade_badge = {"A": " 🟢A", "B": " 🟡B", "C": " 🔴C"}.get(grade, "")

            # hub_keyword 기준 Trends 링크 (넓은 키워드 → 시계열 데이터 풍부)
            hub = sel.get("hub_keyword", "")
            if hub:
                trends_url = (
                    "https://trends.google.com/trends/explore"
                    f"?q={urllib.parse.quote(hub)}&geo=US&hl=en"
                )
                trends_btn = f" &nbsp;[→ Trends]({trends_url})"
                all_hub_keywords.append(hub)
            else:
                trends_btn = ""

            # Grade 후 검증 키워드 요약 표시 (분석 완료된 경우)
            vk = sel.get("verified_keywords", [])
            if vk:
                top_vk = vk[0]
                vk_summary = (f" | 📊 `{top_vk['keyword']}` "
                              f"월 {top_vk['monthly_searches']:,}")
            else:
                vk_summary = ""

            st.markdown(
                f"**{info['folder_name']}**{grade_badge}{trends_btn}  \n"
                f"&nbsp;&nbsp;시계열 {ts} · 상위검색 {tp} · 급상승 {rs} "
                f"· Trends/KP 검색: `{hub}`{vk_summary}",
                unsafe_allow_html=False)

        kp_status = f"✅ {os.path.basename(scan['kp_files'][-1])}" if scan["kp_files"] \
                    else "⬜ 없음 (keyword_planner_*.csv 또는 Keyword_Stats_*.csv)"
        st.markdown(f"**Keyword Planner CSV (주차 루트):** {kp_status}")

        # KP 입력용 hub 키워드 복사 박스
        if all_hub_keywords:
            unique_hubs = list(dict.fromkeys(all_hub_keywords))
            st.text_area(
                "📋 KP 입력 키워드 — hub 기준으로 검색해야 롱테일 발굴 가능",
                value="\n".join(unique_hubs),
                height=120,
                key="kp_keywords_box",
                help="넓은 hub 키워드 → KP가 연관 롱테일 제안 → LOW경쟁+월100이상만 포스팅 키워드로 자동 채택"
            )

        if st.button("📈 CSV 분석 실행 (Grade 판정)", type="primary", key="run_trends"):
            with st.spinner("CSV 분석 중..."):
                try:
                    report = analyze_week(week_tag)
                    st.success(f"분석 완료 — KP 키워드 {report['kp_parsed']}개 파싱")
                    if report.get("kp_error"):
                        st.warning(f"KP: {report['kp_error']}")

                    for c in report["clusters"]:
                        icon = {"A": "🟢", "B": "🟡", "C": "🔴"}.get(c["grade"], "⬜")
                        with st.expander(
                            f"{icon} Grade {c['grade']} — {c['cluster_name']}",
                            expanded=True
                        ):
                            # 판정 근거
                            for reason in c.get("grade_reasons", []):
                                if "✅" in reason:
                                    st.success(reason)
                                elif "❌" in reason:
                                    st.error(reason)
                                elif "⚠️" in reason:
                                    st.warning(reason)
                                else:
                                    st.info(reason)

                            # 검증 키워드 TOP
                            if c["verified_keywords"]:
                                st.markdown("**검증된 키워드 (write_prompt에 자동 삽입):**")
                                for v in c["verified_keywords"][:5]:
                                    comp_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(
                                        v.get("competition", ""), "⬜")
                                    st.markdown(
                                        f"&nbsp;&nbsp;{comp_color} `{v['keyword']}` "
                                        f"— 월 **{v['monthly_searches']:,}** | "
                                        f"경쟁: {v.get('competition','?')}")

                            # 급상승 검색어
                            if c.get("rising_queries"):
                                rising = ", ".join(
                                    f"`{q['query']}`" for q in c["rising_queries"][:3])
                                st.markdown(f"**급상승 검색어:** {rising}")

                            # 경고
                            for w in c["warnings"]:
                                st.warning(w)

                    if report["unassigned_keywords"]:
                        st.caption("미배정 KP 키워드: "
                                   + ", ".join(report["unassigned_keywords"][:8]))
                    st.rerun()
                except Exception as e:
                    st.error(f"분석 실패: {e}")

# ── 이하 탭들은 candidate 기획안 기준 ──
candidates        = get_candidates()                          # 전체 (현황 탭용)
candidates_todo   = get_candidates(exclude_done=True)         # 미완료 (글쓰기 탭)
candidates_review = get_candidates(min_stage=2, max_stage=4)  # 초안 있음 + 미발행 (검증 탭)
candidates_pub    = get_candidates(min_stage=5, max_stage=5)  # 최종본 완료 + 미발행 (발행 탭)

def find_selection_data(cluster_name):
    """weekly_selections에서 클러스터의 최신 선택 데이터(grade 등) 조회."""
    data = load_pipeline()
    for week in sorted(data.get("weekly_selections", {}).keys(), reverse=True):
        for s in data["weekly_selections"][week]:
            if s.get("cluster_name") == cluster_name:
                return s
    return None


def cluster_selector(key, mode="all"):
    """mode: 'all' | 'write' | 'review' | 'pub'"""
    pool = {
        "write":  candidates_todo,
        "review": candidates_review,
        "pub":    candidates_pub,
    }.get(mode, candidates)

    done_msg = {
        "write":  "✅ 모든 기획안의 최종본이 완료됐어요!",
        "review": "✅ 검증할 초안이 없어요. 글쓰기 탭에서 초안을 먼저 저장하세요.",
        "pub":    "✅ 발행할 최종본이 없어요. 검증+수정 탭에서 최종본을 먼저 저장하세요.",
    }.get(mode, "")

    if not pool:
        if done_msg:
            st.info(done_msg)
        else:
            st.warning("발행 대기 기획안이 없어요. [기획] 탭에서 먼저 선택하세요.")
        return None, None
    options = {f"{c['cluster']} ({c['type']}, {c['timing']})": c for c in pool}
    label   = st.selectbox("작업할 기획안", list(options.keys()), key=key)
    sel     = options[label]
    return sel, slugify(sel["cluster"])

# =====================================================================
# 탭: 글쓰기
# =====================================================================
with tab_write:
    sel, slug = cluster_selector("write_sel", mode="write")
    if sel:
        stage_num, stage_msg = get_stage(slug, sel.get("type", ""))
        st.info(stage_msg)

        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("#### ⚙️ 원문 수집 + 프롬프트 생성")

            # Grade 표시 + Grade C 게이트
            sel_data  = find_selection_data(sel["cluster"])
            grade     = sel_data.get("data_grade", "") if sel_data else ""
            pattern   = sel_data.get("trends_pattern", "UNKNOWN") if sel_data else "UNKNOWN"
            vk_count  = len(sel_data.get("verified_keywords", [])) if sel_data else 0
            force_prep = True
            if grade:
                icon = {"A": "🟢", "B": "🟡", "C": "🔴"}.get(grade, "⬜")
                st.markdown(f"{icon} **Grade {grade}** | Trends: {pattern} | "
                            f"검증 키워드: {vk_count}개")
                if grade == "C":
                    st.warning("Trends/KP 검증 데이터가 없어요. 원칙적으로 발행 보류 대상이에요.")
                    force_prep = st.checkbox("⚠️ 미검증 상태로 진행", key="force_prep")

            mode = st.radio("수집 모드", ["jina (다단계 원문 수집)", "title (제목만)"],
                            horizontal=True, key="prep_mode")
            if st.button("🚀 prep 실행", type="primary", key="run_prep",
                         disabled=(grade == "C" and not force_prep)):
                with st.spinner("원문 수집 중... (1~3분 소요)"):
                    ok, log = run_captured(
                        cmd_prep, sel["cluster"],
                        mode="jina" if mode.startswith("jina") else "title",
                        force=force_prep,
                        content_type=sel.get("type", ""))
                # session_state에 로그 저장 (rerun 후에도 유지)
                st.session_state["prep_log"]    = log
                st.session_state["prep_ok"]     = ok
                st.session_state["prep_cluster"] = sel["cluster"]

            # 로그 표시 (rerun 없이 session_state에서 읽기)
            if st.session_state.get("prep_cluster") == sel["cluster"] and \
               "prep_log" in st.session_state:
                with st.expander("실행 로그", expanded=True):
                    st.code(st.session_state["prep_log"], language=None)
                if st.session_state.get("prep_ok"):
                    st.success("✅ 프롬프트 생성 완료")
                else:
                    st.warning("⚠️ 일부 오류가 있었지만 프롬프트는 저장됐을 수 있어요. 로그 확인하세요.")

            # content_type 포함된 파일만 정확히 찾기
            _ct_tag = sel.get("type", "").upper()
            _prompt_pattern = (f"write_prompt_{slug}_{_ct_tag}_*.txt"
                               if _ct_tag else f"write_prompt_{slug}_*.txt")
            prompts = sorted(Path(PROMPTS_DIR).glob(_prompt_pattern),
                             reverse=True) if os.path.exists(PROMPTS_DIR) else []
            if prompts:
                with open(prompts[0], encoding="utf-8") as f:
                    prompt_text = f.read()
                st.markdown("#### 📤 Gemini에 복사할 프롬프트")
                st.caption(f"{prompts[0].name} ({len(prompt_text.encode())/1024:.1f} KB) — 우측 상단 복사 버튼")
                st.code(prompt_text, language=None)
            elif stage_num >= 5:
                st.info("✅ 이 기획안은 최종본 완료 상태예요.")

        with col_r:
            st.markdown("#### 📥 Gemini 초안 붙여넣기")
            draft_input = st.text_area("초안 전체 붙여넣기", height=400, key=f"draft_{slug}")

            # 실시간 품질 검사 — 내용이 있으면 즉시 분석
            if draft_input.strip():
                stripped = draft_input.strip()
                if stripped.startswith("[{") or stripped.startswith('[\n{'):
                    st.error("❌ JSON이 감지됐어요. Gemini 초안(마크다운 글)을 붙여넣어야 해요.")
                else:
                    cleaned = extract_markdown_block(clean_markdown_escapes(draft_input))
                    qr = check_draft_quality(cleaned)

                    # 결과 표시
                    if not qr["ok"]:
                        st.error(f"🚫 품질 게이트 차단 — 저장 불가")
                        for e in qr["errors"]:
                            st.error(f"❌ {e}")
                    else:
                        if qr["warnings"]:
                            for w in qr["warnings"]:
                                st.warning(f"⚠️ {w}")
                        else:
                            st.success(f"✅ 품질 통과 — {qr['word_count']}단어")

                    col_save, col_discard = st.columns(2)
                    with col_save:
                        save_disabled = not qr["ok"]
                        if st.button("💾 저장", type="primary",
                                     key=f"sd_{slug}", disabled=save_disabled):
                            os.makedirs(DRAFTS_DIR, exist_ok=True)
                            _dct = sel.get("type", "").upper()
                            _dfname = f"{slug}_{_dct}.md" if _dct else f"{slug}.md"
                            (Path(DRAFTS_DIR) / _dfname).write_text(cleaned, encoding="utf-8")
                            st.rerun()
                    with col_discard:
                        if st.button("🗑️ 폐기", type="secondary", key=f"discard_btn_{slug}"):
                            st.session_state[f"show_discard_{slug}"] = True

                    # 폐기 확정 UI
                    if st.session_state.get(f"show_discard_{slug}"):
                        discard_reason = st.text_input(
                            "폐기 사유", value="품질 게이트 실패 — 수동 폐기",
                            key=f"discard_reason_{slug}")
                        if st.button("⚠️ 폐기 확정", key=f"do_discard_{slug}"):
                            ok = discard_cluster(
                                sel.get("cluster", slug),
                                content_type=sel.get("type", ""),
                                reason=discard_reason)
                            if ok:
                                st.success("🗑️ 폐기 완료")
                                st.session_state.pop(f"show_discard_{slug}", None)
                                st.rerun()
                            else:
                                st.error("폐기 실패 — 이미 폐기됐거나 candidate 상태가 아닙니다")
            else:
                # 아직 입력 없음 — 저장 버튼만 비활성으로 표시
                st.button("💾 저장", type="primary", key=f"sd_{slug}", disabled=True)

            _dct2 = sel.get("type", "").upper()
            _dfname2 = f"{slug}_{_dct2}.md" if _dct2 else f"{slug}.md"
            if (Path(DRAFTS_DIR) / _dfname2).exists():
                st.success("✅ 초안 저장됨 → [검증+수정] 탭으로")

# =====================================================================
# 탭: 검증+수정
# =====================================================================
with tab_review:
    sel, slug = cluster_selector("review_sel", mode="review")
    if sel:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("#### ⚙️ 검증+수정 프롬프트 생성")
            _rct2 = sel.get("type", "").upper()
            _rdfname = f"{slug}_{_rct2}.md" if _rct2 else f"{slug}.md"
            draft_exists = (Path(DRAFTS_DIR) / _rdfname).exists()
            if not draft_exists:
                st.warning("초안이 없어요. [글쓰기] 탭에서 먼저 저장하세요.")
            if st.button("🚀 review 실행", type="primary",
                         disabled=not draft_exists, key="run_review"):
                ok, log = run_captured(cmd_review, sel["cluster"], sel.get("type", ""))
                with st.expander("실행 로그", expanded=not ok):
                    st.code(log, language=None)
                if ok:
                    st.success("review 프롬프트 생성 완료")
                    st.rerun()

            _rct = sel.get("type", "").upper()
            review_path = Path(PROMPTS_DIR) / (
                f"review_prompt_{slug}_{_rct}.txt" if _rct
                else f"review_prompt_{slug}.txt")
            if review_path.exists():
                with open(review_path, encoding="utf-8") as f:
                    review_text = f.read()
                st.markdown("#### 📤 Claude에 복사할 프롬프트")
                st.caption(f"{review_path.name} ({len(review_text.encode())/1024:.1f} KB)")
                st.code(review_text, language=None)

        with col_r:
            st.markdown("#### 📥 Claude 최종본 붙여넣기")
            st.caption("markdown 코드블록 포함해서 붙여넣어도 자동 추출돼요")
            final_input = st.text_area("최종본 붙여넣기", height=400, key=f"final_{slug}")
            if st.button("💾 최종본 저장", type="primary", key=f"sf_{slug}"):
                if final_input.strip():
                    os.makedirs(FINAL_DIR, exist_ok=True)
                    cleaned = extract_markdown_block(clean_markdown_escapes(final_input))
                    _fct = sel.get("type", "").upper()
                    _ffname = f"{slug}_{_fct}.md" if _fct else f"{slug}.md"
                    path = Path(FINAL_DIR) / _ffname
                    path.write_text(cleaned, encoding="utf-8")
                    st.success(f"저장 완료 ({len(cleaned.split())}단어)")

                    # ── 발행 기록 자동 처리 ──
                    import re as _re
                    h1 = _re.search(r'^# (.+)$', cleaned, _re.MULTILINE)
                    auto_title = h1.group(1).strip() if h1 else sel.get("title", "")
                    # URL은 slug 기반 (TYPE 없이) — 제목이 달라서 URL 충돌 없음
                    # GUIDE: /drafts/steam-machine-hardware-management-guide
                    # COMPARISON: /drafts/steam-machine-hardware-management-comparison
                    _ct_slug = sel.get("type", "").lower()
                    auto_url  = f"/drafts/{slug}-{_ct_slug}" if _ct_slug else f"/drafts/{slug}"
                    sel_data  = find_selection_data(sel["cluster"])
                    try:
                        record_publish(sel["cluster"], auto_title, auto_url,
                                       content_type=sel.get("type", ""))
                        st.info(f"📤 발행 기록 자동 저장: {auto_title[:40]}...")
                    except Exception as _e:
                        st.warning(f"발행 기록 자동 저장 실패 (수동 입력 필요): {_e}")
                    st.rerun()
                else:
                    st.error("내용이 비어있어요")

            _fct2 = sel.get("type", "").upper()
            _ffname2 = f"{slug}_{_fct2}.md" if _fct2 else f"{slug}.md"
            if (Path(FINAL_DIR) / _ffname2).exists():
                st.success("✅ 최종본 저장됨 → 블로그 발행 후 [발행 기록] 탭으로")

# =====================================================================
# 탭: 발행 기록
# =====================================================================
with tab_publish:
    sel, slug = cluster_selector("pub_sel", mode="pub")
    if sel:
        _pct = sel.get("type", "").upper()
        _pfname = f"{slug}_{_pct}.md" if _pct else f"{slug}.md"
        final_path = Path(FINAL_DIR) / _pfname
        if final_path.exists():
            st.success(f"✅ 최종본 준비됨: write/final/{_pfname}")
            with st.expander("최종본 미리보기"):
                st.markdown(final_path.read_text(encoding="utf-8"))
        else:
            st.warning("최종본이 아직 없어요. 발행 기록은 최종본 없이도 가능하지만 권장하지 않아요.")

        st.markdown("#### 📤 발행 완료 기록")
        with st.form(key=f"pub_form_{slug}"):
            pub_title = st.text_input("실제 발행 제목")
            pub_url   = st.text_input("발행 URL")
            submitted = st.form_submit_button("발행 기록 저장", type="primary")

        if submitted:
            if pub_title.strip() and pub_url.strip():
                result = record_publish(sel["cluster"], pub_title.strip(), pub_url.strip())
                if result["ok"]:
                    st.success(f"발행 기록 완료: {result['title']}")
                    if result["updated_week"] and result["updated_week"] != result["week_tag"]:
                        st.info(f"기획 주차 {result['updated_week']} → 발행 주차 {result['week_tag']}")
                    st.metric("발행 완료", f"{result['published_count']}편")
                    st.metric("완결 클러스터", f"{result['completed']}개")
                else:
                    st.error(result["error"])
            else:
                st.error("제목과 URL을 모두 입력하세요")

# =====================================================================
# 탭: 현황
# =====================================================================
with tab_status:
    data      = load_pipeline()
    published = data.get("published", [])
    clusters  = data.get("covered_clusters", {})
    hubs      = data.get("hub_clusters", {})
    completed = sum(1 for c in clusters.values() if len(c.get("types_done", [])) >= 2)
    ready_hubs = [h for h, hc in hubs.items() if hc.get("hub_status") == "READY"]

    # ── 메트릭 ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("발행 완료", f"{len(published)}편")
    c2.metric("대기 기획안", f"{len(candidates)}개")
    c3.metric("허브 클러스터", f"{len(hubs)}개")
    c4.metric("허브 작성 READY", f"{len(ready_hubs)}개",
              delta="작성 가능!" if ready_hubs else None)

    # ── 허브+스포크 현황 ──
    st.divider()
    st.markdown("#### 🔷 허브+스포크 클러스터 현황")
    if not hubs:
        st.info("기획안 선택 기록 시 허브 클러스터가 자동 생성돼요.")
    else:
        for hub_name, hc in hubs.items():
            status = hc.get("hub_status", "PENDING")
            icon   = {"PENDING": "⏳", "READY": "✅", "PUBLISHED": "🟢"}.get(status, "❓")
            spokes     = hc.get("spokes", [])
            spoke_urls = hc.get("spoke_urls", {})
            pub_count  = len(spoke_urls)

            with st.expander(
                f"{icon} **{hub_name}** [{status}] — 스포크 {len(spokes)}개 / 발행 {pub_count}개",
                expanded=(status == "READY")
            ):
                for spoke in spokes:
                    url = spoke_urls.get(spoke, "")
                    cc  = clusters.get(spoke, {})
                    grade = ""
                    # weekly_selections에서 grade 조회
                    for week_sels in data.get("weekly_selections", {}).values():
                        for s in week_sels:
                            if s.get("cluster_name") == spoke:
                                g = s.get("data_grade", "")
                                if g:
                                    grade = f" | Grade {'🟢' if g=='A' else '🟡' if g=='B' else '🔴'}{g}"
                                break
                    pub_icon = "✅" if url else "⬜"
                    ct = cc.get("types_done", [])
                    ct_str = f" [{', '.join(ct)}]" if ct else ""
                    if url:
                        st.markdown(f"&nbsp;&nbsp;{pub_icon} [{spoke}{ct_str}]({url}){grade}")
                    else:
                        st.markdown(f"&nbsp;&nbsp;{pub_icon} {spoke}{ct_str}{grade}")

                if status == "READY":
                    st.success(f"💡 스포크 {pub_count}편 발행 완료 → 허브 글 작성 가능!")
                    if hc.get("internal_links"):
                        st.caption("내부링크 삽입 URL: " +
                                   " | ".join(hc["internal_links"]))

                # 허브 URL 입력
                if status in ("READY", "PUBLISHED"):
                    hub_url_input = st.text_input(
                        "허브 글 URL (발행 후 입력)",
                        value=hc.get("hub_url", ""),
                        key=f"hub_url_{slugify(hub_name)}"
                    )
                    if hub_url_input and hub_url_input != hc.get("hub_url", ""):
                        if st.button("💾 허브 URL 저장", key=f"save_hub_{slugify(hub_name)}"):
                            hc["hub_url"]    = hub_url_input
                            hc["hub_status"] = "PUBLISHED"
                            save_pipeline(data)
                            st.success("허브 발행 기록 완료!")
                            st.rerun()

    # ── 기획안별 진행 상황 ──
    st.divider()
    st.markdown("#### 📋 기획안별 진행 상황")
    if not candidates:
        st.info("대기 중인 기획안이 없어요.")
    else:
        for c in candidates:
            s = slugify(c["cluster"])
            num, msg = get_stage(s, sel.get("type", "") if sel else "")
            # Grade 표시
            sel_data = find_selection_data(c["cluster"])
            grade    = sel_data.get("data_grade", "") if sel_data else ""
            parent   = sel_data.get("parent_hub", "") if sel_data else ""
            grade_txt = f" | Grade {'🟢' if grade=='A' else '🟡' if grade=='B' else '🔴' if grade=='C' else ''}{''+grade if grade else ''}" if grade else ""
            parent_txt = f" | 허브: *{parent}*" if parent else ""
            st.markdown(f"**{c['cluster']}**{grade_txt}{parent_txt} — {msg}")
            st.progress(num / 5)

    # ── [INTERNAL LINK] 플레이스홀더 관리 (posts.json 기반) ──
    st.divider()
    st.markdown("#### 🔗 [INTERNAL LINK] 플레이스홀더 현황")
    if _PM_OK:
        unresolved = get_unresolved_links()
        if not unresolved:
            st.success("✅ 모든 내부링크 교체 완료 (또는 발행된 글 없음)")
        else:
            st.warning(f"⚠️ {len(unresolved)}건의 INTERNAL LINK 미교체")
            for item in unresolved:
                post    = item["post"]
                pending = item["pending"]
                st.markdown(f"**{post['title']}** ({post['status']})")
                for p in pending:
                    # 해당 허브 URL 찾기
                    hub_url = ""
                    for hub_name, hc in hubs.items():
                        if hub_name.lower() in p.lower():
                            hub_url = hc.get("hub_url", "")
                            break
                    if hub_url:
                        st.markdown(f"&nbsp;&nbsp;→ `{p}` ✅ 교체 가능: {hub_url}")
                        if st.button(f"🔄 링크 교체", key=f"resolve_{post['id']}"):
                            changed = resolve_internal_links(hub_name, hub_url)
                            st.success(f"{len(changed)}개 파일 교체 완료")
                            st.rerun()
                    else:
                        st.markdown(f"&nbsp;&nbsp;→ `{p}` ⬜ 허브 URL 미등록")
    else:
        st.info("posts_manager.py 없음 — 플레이스홀더 관리 비활성화")

    # ── 최근 발행 (posts.json 기반) ──
    st.divider()
    st.markdown("#### 📅 전체 글 목록")
    if _PM_OK:
        posts_data = load_posts()
        all_posts  = posts_data.get("posts", [])
        if not all_posts:
            st.info("발행된 글이 없어요.")
        else:
            hub_summary = get_hub_summary()
            for hub_name, info in hub_summary.items():
                with st.expander(
                    f"🔷 {hub_name} ({info['live']}/{len(info['spokes'])}편 라이브)",
                    expanded=False
                ):
                    for p in info["spokes"]:
                        icon = {"draft_url": "⬜", "live": "✅",
                                "internal_linked": "🔗"}.get(p["status"], "❓")
                        pending = (len(p.get("internal_links_needed", [])) -
                                   len(p.get("internal_links_resolved", {})))
                        link_txt = f" ⚠️{pending}개 링크 미교체" if pending > 0 else ""
                        grade = p.get("data_grade", "")
                        grade_txt = f" | Grade {grade}" if grade else ""
                        live_url = p.get("live_url", "") or p.get("url", "")

                        col1, col2 = st.columns([4, 2])
                        with col1:
                            if live_url and not live_url.startswith("/drafts"):
                                st.markdown(f"{icon} [{p['title']}]({live_url}){grade_txt}{link_txt}")
                            else:
                                st.markdown(f"{icon} {p['title']}{grade_txt}{link_txt}")
                        with col2:
                            new_url = st.text_input(
                                "실제 URL", value=live_url,
                                key=f"url_{p['id']}",
                                placeholder="/posts/slug"
                            )
                            if new_url and new_url != live_url:
                                if st.button("저장", key=f"save_url_{p['id']}"):
                                    update_live_url(p["id"], new_url)
                                    st.rerun()
    else:
        if published:
            for p in reversed(published[-8:]):
                hub = p.get("hub_cluster", "")
                hub_txt = f" | 허브: *{hub}*" if hub else ""
                st.markdown(f"- [{p.get('week_tag','')}] {p.get('title','')}{hub_txt}")

    st.divider()
    st.caption("터미널이 여전히 필요한 것: research.py (주간), "
               "monthly_analysis.py (월간), 그리고 이 앱 실행 자체. "
               "이들은 Phase 3에서 GitHub Actions로 자동화 예정.")
