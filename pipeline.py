# =====================================================================
# 📋 파이프라인 관리 (pipeline.py) — v2
# =====================================================================
import os
import re
import json
from datetime import datetime, timezone

PIPELINE_FILE = "content_pipeline.json"
TYPE_SEQUENCE = ["COMPARISON", "GUIDE", "EXPLAINER", "LISTICLE"]


def load_pipeline():
    try:
        with open(PIPELINE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"hub_clusters": {}, "covered_clusters": {},
                "weekly_selections": {}, "published": []}


def save_pipeline(data):
    data["_last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(PIPELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ content_pipeline.json 저장 완료")


def get_suggest_next(cluster_name, data):
    cc   = data.get("covered_clusters", {}).get(cluster_name, {})
    done = cc.get("types_done", [])
    remaining = [t for t in TYPE_SEQUENCE if t not in done]
    return remaining


def build_covered_summary(data):
    lines = []
    for name, info in data.get("covered_clusters", {}).items():
        done      = info.get("types_done", [])
        suggest   = [t for t in TYPE_SEQUENCE if t not in done]
        hub       = info.get("hub_keyword", "")
        parent    = info.get("parent_hub", hub)
        week      = info.get("last_week", "")
        comp      = info.get("competition_level", "")
        trend     = info.get("trends_pattern", "UNKNOWN")
        lines.append(
            f"- {name} [{', '.join(done) if done else 'none done'}, {week}] "
            f"Competition:{comp} Trends:{trend} Hub:\"{hub}\" Parent:\"{parent}\" "
            f"→ suggest next: {', '.join(suggest)}"
        )
    return "\n".join(lines)


# =====================================================================
# hub_keyword 정규화 (Trends/KP 검색에 적합한 넓은 키워드로)
# =====================================================================

def _normalize_hub_keyword(hub_keyword):
    """
    hub_keyword를 넓은 검색 기준으로 정규화.
    마지막 단어가 일반 수식어면 제거.
    예: "Steam Machine Verified" → "Steam Machine"
        "Samsung Health Backup" → "Samsung Health"
        "Chrome Manifest V2"   → "Chrome Manifest V2" (버전 번호 유지)
    """
    words = hub_keyword.strip().split()
    if len(words) <= 2:
        return hub_keyword
    generic_suffixes = {
        "backup", "guide", "setup", "fix", "overheating",
        "malware", "beta", "feature", "features", "review",
        "comparison", "tutorial", "update", "security", "protection",
    }
    if words[-1].lower() in generic_suffixes:
        return " ".join(words[:-1])
    return hub_keyword


# =====================================================================
# 선택 기록
# =====================================================================

def record_selections(selections, week_tag=None):
    """
    기획안 선택 기록.
    parent_hub: 이 스포크가 속하는 허브 클러스터 이름
                미지정 시 normalize된 hub_keyword 사용
    """
    data = load_pipeline()
    now  = datetime.now(timezone.utc)
    if not week_tag:
        week_tag = now.strftime("%Y-W%W")

    if "hub_clusters" not in data:
        data["hub_clusters"] = {}

    recorded = []
    for sel in selections:
        cluster = sel.get("cluster_name", "").strip()
        if not cluster:
            continue

        raw_hub    = sel.get("hub_keyword", "")
        norm_hub   = _normalize_hub_keyword(raw_hub)
        parent_hub = sel.get("parent_hub", norm_hub)

        # 방식 C: 기존 hub_clusters와 정확 매칭 → 자동 귀속
        # 1) Gemini 제안 parent_hub가 기존 허브와 정확 일치
        # 2) norm_hub가 기존 허브와 정확 일치
        # 3) 둘 다 없으면 새로 생성
        existing_hubs = list(data["hub_clusters"].keys())
        if parent_hub not in existing_hubs and norm_hub not in existing_hubs:
            # 토큰 유사도로 기존 허브 검색 (정규화 후 비교)
            def _hub_tokens(text):
                tokens = set()
                for t in text.lower().split():
                    # 단복수 정규화 (machines → machine)
                    if len(t) > 3 and t.endswith("s"):
                        t = t[:-1]
                    tokens.add(t)
                return tokens
            ph_tokens = _hub_tokens(parent_hub)
            best_hub = None
            best_score = 0
            for eh in existing_hubs:
                eh_tokens = _hub_tokens(eh)
                if not eh_tokens:
                    continue
                overlap = len(ph_tokens & eh_tokens) / max(len(ph_tokens), len(eh_tokens))
                if overlap >= 0.8 and overlap > best_score:
                    best_score = overlap
                    best_hub = eh
            if best_hub:
                parent_hub = best_hub  # 기존 허브에 자동 귀속
        elif norm_hub in existing_hubs and parent_hub not in existing_hubs:
            parent_hub = norm_hub  # norm_hub가 기존 허브와 일치

        entry = {
            "cluster_name":         cluster,
            "content_type":         sel.get("content_type", "").upper(),
            "suggested_title":      sel.get("suggested_title", ""),
            "hub_keyword":          norm_hub,
            "hub_keyword_raw":      raw_hub,
            "parent_hub":           parent_hub,
            "spoke_keywords":       sel.get("spoke_keywords", []),
            "competition_level":    sel.get("competition_level", "").upper(),
            "timing":               sel.get("timing", "").upper(),
            "affiliate_potential":  sel.get("affiliate_potential", "").upper(),
            "trends_pattern":       sel.get("trends_pattern", "UNKNOWN"),
            "trends_keyword":       sel.get("trends_keyword", ""),
            "trends_opportunities": sel.get("trends_opportunities", []),
            "verifiability":        sel.get("verifiability", "MEDIUM"),
            "data_grade":           sel.get("data_grade", ""),
            "verified_keywords":    sel.get("verified_keywords", []),
            "status":               "candidate",
            "selected_at":          now.isoformat(),
        }
        recorded.append(entry)

        # hub_clusters 자동 생성/업데이트
        if parent_hub not in data["hub_clusters"]:
            data["hub_clusters"][parent_hub] = {
                "hub_keyword":    parent_hub,
                "hub_status":     "PENDING",
                "hub_title":      "",
                "hub_url":        "",
                "spokes":         [],
                "spoke_urls":     {},
                "internal_links": [],
            }
        hc = data["hub_clusters"][parent_hub]
        if cluster not in hc["spokes"]:
            hc["spokes"].append(cluster)
        if len(hc["spokes"]) >= 2 and hc["hub_status"] == "PENDING":
            hc["hub_status"] = "READY"

        # covered_clusters 업데이트
        if cluster not in data["covered_clusters"]:
            data["covered_clusters"][cluster] = {
                "types_done":         [],
                "last_week":          week_tag,
                "suggest_next":       TYPE_SEQUENCE[:],
                "hub_keyword":        norm_hub,
                "parent_hub":         parent_hub,
                "spoke_keywords":     entry["spoke_keywords"],
                "competition_level":  entry["competition_level"],
                "affiliate_potential":entry["affiliate_potential"],
                "trends_pattern":     entry["trends_pattern"],
                "trends_keyword":     entry["trends_keyword"],
                "notes":              "",
            }
        cc = data["covered_clusters"][cluster]
        cc["last_week"]      = week_tag
        cc["trends_pattern"] = entry["trends_pattern"]
        cc["hub_keyword"]    = norm_hub
        cc["parent_hub"]     = parent_hub

    if recorded:
        existing      = data["weekly_selections"].get(week_tag, [])
        existing_keys = {(s.get("cluster_name"), s.get("content_type")) for s in existing}
        new_entries   = [e for e in recorded
                         if (e["cluster_name"], e["content_type"]) not in existing_keys]
        data["weekly_selections"][week_tag] = existing + new_entries
        save_pipeline(data)

        created_folders = _ensure_trends_folders(
            week_tag, data["weekly_selections"][week_tag])

        return {"ok": True, "recorded": len(new_entries),
                "skipped": len(recorded) - len(new_entries),
                "week_tag": week_tag,
                "trends_folders": created_folders}
    return {"ok": False, "error": "기록할 기획안 없음"}


def _slugify(text):
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def _ensure_trends_folders(week_tag, selections):
    week_dir = os.path.join("research_data", "trends", week_tag)
    os.makedirs(week_dir, exist_ok=True)
    folders = []
    seen_slugs = set()
    idx = 0
    for sel in selections:
        slug = _slugify(sel.get("cluster_name", ""))
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        idx += 1
        folder_name = f"{idx:02d}-{slug}"
        os.makedirs(os.path.join(week_dir, folder_name), exist_ok=True)
        folders.append(folder_name)
    return folders


# =====================================================================
# 발행 기록 (write.py의 record_publish가 호출)
# =====================================================================

def record_spoke_publish(cluster_name, url, data):
    """스포크 발행 시 hub_clusters의 spoke_urls 업데이트."""
    if "hub_clusters" not in data:
        return
    cc = data.get("covered_clusters", {}).get(cluster_name, {})
    parent_hub = cc.get("parent_hub", "")
    if parent_hub and parent_hub in data["hub_clusters"]:
        hc = data["hub_clusters"][parent_hub]
        hc["spoke_urls"][cluster_name] = url
        hc["internal_links"] = list(hc["spoke_urls"].values())
        # 스포크 2편 이상 발행됐으면 허브 READY 확인
        if len(hc["spoke_urls"]) >= 2 and hc["hub_status"] in ("PENDING", "READY"):
            hc["hub_status"] = "READY"


# =====================================================================
# CLI
# =====================================================================

def cmd_select():
    data     = load_pipeline()
    now      = datetime.now(timezone.utc)
    week_tag = now.strftime("%Y-W%W")
    print(f"\n📝 기획안 선택 기록 — {week_tag}\n(완료: 빈 줄 Enter)\n")
    selections = []
    idx = 1
    while True:
        print(f"[{idx}번 기획안]")
        cluster = input("  클러스터명: ").strip()
        if not cluster:
            break
        ct   = input("  유형 (COMPARISON/GUIDE/EXPLAINER/LISTICLE): ").strip().upper()
        hub  = input("  hub_keyword (넓은 검색어): ").strip()
        ph   = input(f"  parent_hub (허브 클러스터명, 기본={hub}): ").strip() or hub
        comp = input("  competition_level (LOW/MEDIUM/HIGH): ").strip().upper()
        veri = input("  verifiability (HIGH/MEDIUM): ").strip().upper()
        selections.append({
            "cluster_name": cluster, "content_type": ct,
            "hub_keyword": hub, "parent_hub": ph,
            "competition_level": comp, "verifiability": veri,
            "timing": "NOW",
        })
        idx += 1
    if selections:
        result = record_selections(selections, week_tag)
        print(f"✅ {result}")


def cmd_status():
    data = load_pipeline()
    print(f"\n{'='*55}")
    print(f"📊 파이프라인 현황")
    print(f"{'='*55}")

    # 허브 클러스터 현황
    hubs = data.get("hub_clusters", {})
    print(f"\n🔷 허브 클러스터 ({len(hubs)}개)")
    for hub_name, hc in hubs.items():
        status_icon = {"PENDING": "⏳", "READY": "✅", "PUBLISHED": "🟢"}.get(
            hc["hub_status"], "❓")
        print(f"  {status_icon} [{hc['hub_status']}] {hub_name}")
        for spoke in hc["spokes"]:
            url = hc["spoke_urls"].get(spoke, "")
            pub = "✅" if url else "⬜"
            print(f"      {pub} {spoke}" + (f" → {url}" if url else ""))
        if hc["hub_status"] == "READY" and not hc["hub_url"]:
            print(f"      💡 허브 글 작성 가능!")

    # 발행 현황
    published = data.get("published", [])
    print(f"\n📝 발행 완료: {len(published)}편")
    for p in published[-5:]:
        print(f"  - [{p.get('week_tag','')}] {p.get('title','')} — {p.get('url','')}")


def cmd_publish():
    pass


def cmd_summary():
    data = load_pipeline()
    print(build_covered_summary(data))


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"select": cmd_select, "status": cmd_status, "summary": cmd_summary}.get(
        cmd, cmd_status)()
