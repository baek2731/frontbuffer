# =====================================================================
# 📸 Frontbuffer OG 이미지 + 트윗 문구 생성기 (og_generator.py)
# =====================================================================
# 동작:
#   1. _posts/ 폴더에서 MD 파일 목록 스캔
#   2. output/ 에 이미 처리된 파일 스킵
#   3. 미처리 파일 → OG 이미지 PNG + 트윗 문구 txt 생성
#
# 사용법:
#   python og_generator.py              → 전체 미처리 파일 자동 처리
#   python og_generator.py --all        → 이미 처리된 것도 재생성
#   python og_generator.py --file 파일명 → 특정 파일만 처리
#
# 필요:
#   pip install cairosvg
#
# 폴더 구조:
#   frontbuffer-social/
#   ├── og_generator.py
#   ├── _posts/          ← _posts/ 폴더 복붙 또는 git pull
#   └── output/          ← 생성된 PNG + txt
# =====================================================================

import os
import re
import sys
import textwrap
import argparse
from pathlib import Path
from datetime import datetime

try:
    import cairosvg
except ImportError:
    print("❌ cairosvg 없음 — pip install cairosvg 실행하세요.")
    sys.exit(1)

POSTS_DIR  = "_posts"
OUTPUT_DIR = "social_output"

# OG 이미지 규격 (Twitter/X 권장)
OG_WIDTH  = 1200
OG_HEIGHT = 630

# 카테고리 키워드
GAMING_KEYS = ["steam", "game", "gaming", "xbox", "playstation",
               "nintendo", "fallout", "portable", "handheld", "deck"]


# ── 유틸 ──────────────────────────────────────────────────────────────

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60]


def parse_md(filepath):
    """MD 파일에서 제목 / 카테고리 / 첫 문단 추출."""
    text = Path(filepath).read_text(encoding="utf-8")

    # front matter 파싱
    title    = ""
    category = "TECH"
    excerpt  = ""

    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        t  = re.search(r"^title:\s*['\"]?(.+?)['\"]?\s*$", fm, re.MULTILINE)
        if t:
            title = t.group(1).strip().strip("'\"")
        e = re.search(r"^excerpt:\s*['\"]?(.+?)['\"]?\s*$", fm, re.MULTILINE)
        if e:
            excerpt = e.group(1).strip().strip("'\"")
        c = re.search(r"^categories:\s*\[(.+?)\]", fm, re.MULTILINE)
        if c:
            cats = c.group(1).lower()
            category = "GAMING" if "gaming" in cats else "TECH"

    # front matter 없으면 H1에서 제목 추출
    if not title:
        h1 = re.search(r"^# (.+)$", text, re.MULTILINE)
        if h1:
            title = h1.group(1).strip()

    # excerpt 없으면 본문 첫 문단
    if not excerpt:
        body = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)
        body = re.sub(r"^#.+$", "", body, flags=re.MULTILINE)
        body = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", body)
        lines = [l.strip() for l in body.splitlines() if l.strip()]
        if lines:
            raw = lines[0]
            excerpt = raw[:120].rsplit(" ", 1)[0] + "…" if len(raw) > 120 else raw

    # 카테고리 키워드로 재판정
    slug_check = slugify(title)
    if any(k in slug_check for k in GAMING_KEYS):
        category = "GAMING"

    return title, category, excerpt


def wrap_svg_text(text, max_chars=32):
    """SVG용 텍스트 줄바꿈 — 최대 2줄."""
    if len(text) <= max_chars:
        return [text]
    words  = text.split()
    lines  = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = (current + " " + word).strip()
        else:
            if current:
                lines.append(current)
            current = word
        if len(lines) == 1 and current:
            # 2줄 초과 방지 — 남은 내용 줄임
            pass
    if current:
        lines.append(current)
    # 최대 2줄
    if len(lines) > 2:
        lines = lines[:2]
        lines[-1] = lines[-1][:max_chars - 1] + "…"
    return lines


def generate_svg(title, category, excerpt):
    """Frontbuffer 브랜드 OG 이미지 SVG 생성."""
    title_lines   = wrap_svg_text(title, max_chars=30)
    excerpt_lines = wrap_svg_text(excerpt, max_chars=52)

    # 제목 y 위치 (줄 수에 따라 조정)
    title_start_y = 280 if len(title_lines) == 1 else 255

    # 제목 SVG 텍스트 블록
    title_svgs = ""
    for i, line in enumerate(title_lines):
        y = title_start_y + i * 62
        title_svgs += f'<text x="80" y="{y}" font-family="Arial, Helvetica, sans-serif" font-weight="700" font-size="52" fill="#ffffff" letter-spacing="-1">{line}</text>\n'

    # excerpt y 위치
    excerpt_start_y = title_start_y + len(title_lines) * 62 + 30
    excerpt_svgs = ""
    for i, line in enumerate(excerpt_lines):
        y = excerpt_start_y + i * 30
        excerpt_svgs += f'<text x="80" y="{y}" font-family="Arial, Helvetica, sans-serif" font-weight="300" font-size="22" fill="#8899aa" letter-spacing="0.3">{line}</text>\n'

    # 카테고리 뱃지 색상
    badge_fill   = "#0f2a1e" if category == "GAMING" else "#0a1a2e"
    badge_stroke = "#2ec4b0"

    svg = f"""<svg width="{OG_WIDTH}" height="{OG_HEIGHT}" xmlns="http://www.w3.org/2000/svg">

  <!-- 배경 -->
  <rect width="{OG_WIDTH}" height="{OG_HEIGHT}" fill="#1a2035"/>

  <!-- 그리드 라인 -->
  <line x1="0" y1="157" x2="{OG_WIDTH}" y2="157" stroke="#ffffff" stroke-width="0.5" opacity="0.04"/>
  <line x1="0" y1="315" x2="{OG_WIDTH}" y2="315" stroke="#ffffff" stroke-width="0.5" opacity="0.04"/>
  <line x1="0" y1="472" x2="{OG_WIDTH}" y2="472" stroke="#ffffff" stroke-width="0.5" opacity="0.04"/>
  <line x1="300" y1="0" x2="300" y2="{OG_HEIGHT}" stroke="#ffffff" stroke-width="0.5" opacity="0.04"/>
  <line x1="600" y1="0" x2="600" y2="{OG_HEIGHT}" stroke="#ffffff" stroke-width="0.5" opacity="0.04"/>
  <line x1="900" y1="0" x2="900" y2="{OG_HEIGHT}" stroke="#ffffff" stroke-width="0.5" opacity="0.04"/>

  <!-- 우측 장식 원 -->
  <circle cx="1050" cy="315" r="320" fill="none" stroke="#2ec4b0" stroke-width="0.6" opacity="0.1"/>
  <circle cx="1050" cy="315" r="220" fill="none" stroke="#2ec4b0" stroke-width="0.6" opacity="0.08"/>
  <circle cx="1050" cy="315" r="120" fill="none" stroke="#2ec4b0" stroke-width="0.6" opacity="0.06"/>

  <!-- 좌측 상단 브랜드 -->
  <text x="80" y="90" font-family="Arial, Helvetica, sans-serif" font-weight="700" font-size="28" fill="#2ec4b0" letter-spacing="1">FRONTBUFFER</text>
  <text x="83" y="118" font-family="Arial, Helvetica, sans-serif" font-weight="400" font-size="16" fill="#5a6a7a" letter-spacing="3">EDITORIAL</text>

  <!-- 구분선 -->
  <line x1="80" y1="140" x2="500" y2="140" stroke="#2ec4b0" stroke-width="1" opacity="0.3"/>

  <!-- 제목 -->
  {title_svgs}

  <!-- excerpt -->
  {excerpt_svgs}

  <!-- 카테고리 뱃지 -->
  <rect x="80" y="560" width="120" height="36" rx="6" fill="{badge_fill}" stroke="{badge_stroke}" stroke-width="1.5"/>
  <text x="140" y="583" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-weight="700" font-size="14" fill="#2ec4b0" letter-spacing="2">{category}</text>

  <!-- 우측 하단 도메인 -->
  <text x="1120" y="590" text-anchor="end" font-family="Arial, Helvetica, sans-serif" font-weight="400" font-size="18" fill="#2ec4b0" opacity="0.5" letter-spacing="1">frontbuffer.net</text>

</svg>"""
    return svg


def generate_tweet(title, category, excerpt, url_slug):
    """트윗 문구 3가지 버전 생성."""
    hashtags_tech   = "#Tech #Chrome #Google #Browser"
    hashtags_gaming = "#Gaming #Steam #PCGaming #Valve"
    hashtags = hashtags_gaming if category == "GAMING" else hashtags_tech

    url_placeholder = f"https://frontbuffer.net/{'gaming' if category == 'GAMING' else 'tech'}/{url_slug}/"

    tweet1 = f"{excerpt}\n\n{url_placeholder}\n\n{hashtags}"
    tweet2 = f"{title}\n\n{url_placeholder}\n\n{hashtags}"
    tweet3 = f"New on Frontbuffer:\n{title}\n\n{url_placeholder}\n\n{hashtags}"

    return f"""=== 트윗 문구 3가지 버전 ===
제목: {title}
카테고리: {category}
URL: {url_placeholder}

---[ 버전 1 — excerpt 중심 ]---
{tweet1}

---[ 버전 2 — 제목 중심 ]---
{tweet2}

---[ 버전 3 — 브랜드 중심 ]---
{tweet3}

해시태그 추가 옵션:
  TECH:   #SEO #WebDev #Developer #ChromeExtensions
  GAMING: #IndieGaming #GameDev #SteamDeck #PCMaster
"""


def process_file(md_path, force=False):
    """단일 MD 파일 처리."""
    stem      = Path(md_path).stem
    out_png   = os.path.join(OUTPUT_DIR, f"og_{stem}.png")
    out_tweet = os.path.join(OUTPUT_DIR, f"tweet_{stem}.txt")

    # 이미 처리됐으면 스킵 (--all 플래그 없으면)
    if not force and os.path.exists(out_png) and os.path.exists(out_tweet):
        print(f"  ✅ 이미 처리됨 — 스킵: {stem}")
        return False

    print(f"  🆕 처리 중: {stem}")

    # MD 파싱
    title, category, excerpt = parse_md(md_path)
    if not title:
        print(f"  ⚠️ 제목 추출 실패 — 스킵: {stem}")
        return False

    print(f"     제목: {title[:50]}...")
    print(f"     카테고리: {category}")

    # URL 슬러그 추출 (파일명에서 날짜 제거)
    url_slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)

    # SVG 생성
    svg_text = generate_svg(title, category, excerpt)

    # PNG 변환
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cairosvg.svg2png(
        bytestring=svg_text.encode("utf-8"),
        write_to=out_png,
        output_width=OG_WIDTH,
        output_height=OG_HEIGHT
    )
    print(f"     📸 PNG 저장: {out_png}")

    # 트윗 문구 저장
    tweet_text = generate_tweet(title, category, excerpt, url_slug)
    Path(out_tweet).write_text(tweet_text, encoding="utf-8")
    print(f"     📝 트윗 저장: {out_tweet}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Frontbuffer OG 이미지 + 트윗 문구 생성기")
    parser.add_argument("--all",  action="store_true", help="이미 처리된 파일도 재생성")
    parser.add_argument("--file", default="",          help="특정 파일만 처리 (파일명)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"📸 Frontbuffer OG 생성기")
    print(f"{'='*60}")

    # _posts/ 폴더 확인
    if not os.path.exists(POSTS_DIR):
        print(f"❌ '{POSTS_DIR}' 폴더 없음")
        print(f"   _posts/ 폴더를 이 스크립트와 같은 위치에 복붙하세요.")
        sys.exit(1)

    # 특정 파일 지정
    if args.file:
        target = os.path.join(POSTS_DIR, args.file)
        if not os.path.exists(target):
            # 확장자 없으면 .md 붙여서 재시도
            target = target if target.endswith(".md") else target + ".md"
        if not os.path.exists(target):
            print(f"❌ 파일 없음: {target}")
            sys.exit(1)
        process_file(target, force=True)
        return

    # 전체 처리
    md_files = sorted(Path(POSTS_DIR).glob("*.md"))
    if not md_files:
        print(f"❌ '{POSTS_DIR}' 폴더에 MD 파일 없음")
        sys.exit(1)

    print(f"  _posts/ 파일: {len(md_files)}개\n")

    processed = 0
    skipped   = 0
    for md in md_files:
        result = process_file(str(md), force=args.all)
        if result:
            processed += 1
        else:
            skipped += 1

    print(f"\n{'='*60}")
    print(f"✅ 완료: 신규 {processed}개 / 스킵 {skipped}개")
    print(f"   결과물: {OUTPUT_DIR}/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
