# =====================================================================
# 🔔 Discord 알림 유틸 (notify.py)
# =====================================================================
# 역할: 각 Step에서 Discord 웹훅으로 알림 전송
#
# 사용법:
#   python notify.py <event> [옵션]
#
# 이벤트:
#   step1_done    --week 2026-W29
#   step2_done    --week 2026-W29 --count 8
#   step3_done    --count 11 --stack 10 [--failures "A,B"]
#   step3_fail    --cluster "Steam Machine" --type HUB --reason "prep 실패"
#   step4_done    --title "Chrome Guide" --url "https://..."
#   step4_fail    --reason "final/ 비어있음"
#   step5_done    --auto N --manual N --stack N
#   custom        --title "제목" --body "내용" [--level info|warn|error]
#
# 환경변수:
#   DISCORD_WEBHOOK_URL: Discord 웹훅 URL (GitHub Secrets에서 주입)
#
# 알림 원칙: 사람 액션이 필요하거나 실패했을 때만.
#   step1_done  → CSV 업로드 요청 (사람 액션 필요)
#   step2_done  → 글 생성 완료 보고 (결과 확인용)
#   step3_done  → 스택 잔량 보고 (잔량 3 미만 시 경고)
#   step3_fail  → 항목 실패 (수동 확인 필요)
#   step4_done  → 정상 발행은 무알림 (step4_publish.yml에서 생략 가능)
#   step4_fail  → 발행 실패 (수동 확인 필요)
#   step5_done  → 주간 감사 리포트 (수동 확인 항목 있을 때만)
# =====================================================================

import os
import sys
import json
import argparse
import requests
from datetime import datetime, timezone

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

# ── Discord 색상 코드 ────────────────────────────────────────────────
COLOR = {
    "info":    0x5865F2,   # 파란색
    "success": 0x57F287,   # 초록색
    "warn":    0xFEE75C,   # 노란색
    "error":   0xED4245,   # 빨간색
}

EMOJI = {
    "info":    "ℹ️",
    "success": "✅",
    "warn":    "⚠️",
    "error":   "❌",
}


def send(title: str, body: str, level: str = "info", fields: list = None):
    """Discord embed 메시지 전송."""
    if not WEBHOOK_URL:
        print(f"⚠️  DISCORD_WEBHOOK_URL 없음 — 알림 스킵")
        print(f"   [{level.upper()}] {title}: {body}")
        return False

    embed = {
        "title":       f"{EMOJI.get(level, '')} {title}",
        "description": body,
        "color":       COLOR.get(level, COLOR["info"]),
        "timestamp":   datetime.now(timezone.utc).isoformat(),
        "footer":      {"text": "Frontbuffer Editorial"},
    }
    if fields:
        embed["fields"] = fields

    payload = {"embeds": [embed]}

    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if resp.status_code in (200, 204):
            print(f"🔔 Discord 알림 전송 완료: {title}")
            return True
        else:
            print(f"⚠️  Discord 알림 실패 ({resp.status_code}): {resp.text[:100]}")
            return False
    except Exception as e:
        print(f"⚠️  Discord 알림 예외: {e}")
        return False


# ── 이벤트별 메시지 포맷 ────────────────────────────────────────────

def notify_step1_done(week: str):
    send(
        title="Step 1 완료 — CSV 업로드 해주세요",
        body=(
            f"이번 주(`{week}`) RSS 수집이 완료됐어요.\n\n"
            f"**다음 할 일:**\n"
            f"1. `research_data/weekly/{week}/manual_report.md` 열기\n"
            f"2. Google Trends 키워드 확인 후 CSV 다운로드\n"
            f"3. `research_data/trends/{week}/` 에 업로드\n"
            f"4. Step 2가 자동으로 시작돼요 🚀"
        ),
        level="warn",   # 사람 액션 필요 → 노란색
    )


def notify_step2_done(week: str, count: int):
    send(
        title="Step 2 완료 — 기획안 생성",
        body=f"이번 주(`{week}`) 기획안 **{count}편** 생성 완료.\nStep 3 글 생성이 자동으로 시작돼요.",
        level="success",
    )


def notify_step3_done(count: int, stack: int, failures: list = None,
                      quality_report_path: str = "research_data/write/quality_report.json"):
    """
    Step 3 완료 알림.
    quality_report.json 이 있으면 품질 체크 결과도 함께 전송.
    """
    import os, json as _json
    from pathlib import Path as _Path

    level = "success"
    body  = f"**{count}편** 생성 완료. 현재 final/ 스택: **{stack}편**"

    if stack < 3:
        level = "warn"
        body += f"\n\n⚠️ 스택 잔량 {stack}편 — Step 2/3를 수동으로 실행해 보충하세요."

    fields = []

    # ── 품질 체크 결과 ────────────────────────────────────────────────
    report_path = _Path(quality_report_path)
    if report_path.exists():
        try:
            report = _json.loads(report_path.read_text(encoding="utf-8"))
            ok_count    = report.get("ok", 0)
            issue_count = report.get("issue_count", 0)
            issue_files = report.get("issue_files", [])

            if issue_count == 0:
                fields.append({
                    "name":   "🔍 품질 체크",
                    "value":  f"✅ 전편 이상 없음 ({ok_count}편)",
                    "inline": False,
                })
            else:
                level = "warn"
                # 파일별 이슈 요약 (Discord 필드 value 1024자 제한)
                lines = []
                for f in issue_files:
                    issue_labels = " / ".join(i["label"] for i in f["issues"])
                    lines.append(f"• **{f['name']}**\n  {issue_labels}\n  [GitHub]({f['link']})")

                value = "\n\n".join(lines)
                if len(value) > 1000:
                    value = value[:1000] + "\n…(잘림)"

                fields.append({
                    "name":   f"⚠️ 품질 확인 필요 — {issue_count}편",
                    "value":  value,
                    "inline": False,
                })
        except Exception as e:
            fields.append({
                "name":   "🔍 품질 체크",
                "value":  f"⚠️ 리포트 파싱 실패: {e}",
                "inline": False,
            })
    else:
        fields.append({
            "name":   "🔍 품질 체크",
            "value":  "리포트 없음 (quality_check.py 실행 여부 확인)",
            "inline": False,
        })

    # ── 생성 실패 항목 ────────────────────────────────────────────────
    if failures:
        fields.append({
            "name":   "❌ 생성 실패 항목",
            "value":  "\n".join(f"• {f}" for f in failures),
            "inline": False,
        })
        level = "warn"

    send(
        title="Step 3 완료 — 글 생성 + 품질 체크",
        body=body,
        level=level,
        fields=fields or None,
    )


def notify_step3_fail(cluster: str, content_type: str, reason: str):
    send(
        title="Step 3 항목 실패",
        body=(
            f"**클러스터:** {cluster}\n"
            f"**타입:** {content_type}\n"
            f"**원인:** {reason}\n\n"
            f"수동으로 확인 후 재실행 필요."
        ),
        level="error",
    )


def notify_step4_done(title: str, url: str):
    """정상 발행 — 기본적으로 호출하지 않음 (무알림 원칙). 필요 시 사용."""
    send(
        title="Step 4 발행 완료",
        body=f"**{title}**\n{url}",
        level="success",
    )


def notify_step4_fail(reason: str):
    send(
        title="Step 4 발행 실패",
        body=f"원인: {reason}\n\n수동으로 확인 후 재실행 필요.",
        level="error",
    )


def notify_step5_done(auto: int, manual: int, stack: int):
    """수동 확인 항목이 없으면 알림 생략."""
    if manual == 0 and stack >= 3:
        print("ℹ️  Step 5 이상 없음 — 알림 생략")
        return

    level = "warn" if manual > 0 or stack < 3 else "success"
    body  = f"자동 수정: **{auto}건** | 수동 확인 필요: **{manual}건** | 스택 잔량: **{stack}편**"

    if manual > 0:
        body += "\n\n`research_data/write/audit_report.md` 에서 상세 확인."
    if stack < 3:
        body += f"\n\n⚠️ 스택 잔량 {stack}편 — 보충 필요."

    send(
        title="Step 5 주간 감사 리포트",
        body=body,
        level=level,
    )


def notify_custom(title: str, body: str, level: str = "info"):
    send(title=title, body=body, level=level)


# ── CLI 진입점 ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Discord 알림 유틸")
    parser.add_argument("event", help="이벤트 이름")

    # 공통 옵션
    parser.add_argument("--week",    default="")
    parser.add_argument("--count",   type=int, default=0)
    parser.add_argument("--stack",   type=int, default=0)
    parser.add_argument("--cluster", default="")
    parser.add_argument("--type",    default="")
    parser.add_argument("--reason",  default="")
    parser.add_argument("--title",   default="")
    parser.add_argument("--url",     default="")
    parser.add_argument("--auto",    type=int, default=0)
    parser.add_argument("--manual",  type=int, default=0)
    parser.add_argument("--body",    default="")
    parser.add_argument("--level",   default="info", choices=["info","warn","error","success"])
    # 실패 목록: 쉼표 구분 문자열
    parser.add_argument("--failures", default="")

    args = parser.parse_args()
    event = args.event.lower()

    failures = [f.strip() for f in args.failures.split(",") if f.strip()] if args.failures else []

    if event == "step1_done":
        notify_step1_done(args.week)
    elif event == "step2_done":
        notify_step2_done(args.week, args.count)
    elif event == "step3_done":
        notify_step3_done(args.count, args.stack, failures)
    elif event == "step3_fail":
        notify_step3_fail(args.cluster, args.type, args.reason)
    elif event == "step4_done":
        notify_step4_done(args.title, args.url)
    elif event == "step4_fail":
        notify_step4_fail(args.reason)
    elif event == "step5_done":
        notify_step5_done(args.auto, args.manual, args.stack)
    elif event == "custom":
        notify_custom(args.title, args.body, args.level)
    else:
        print(f"❌ 알 수 없는 이벤트: {event}")
        sys.exit(1)


if __name__ == "__main__":
    main()
