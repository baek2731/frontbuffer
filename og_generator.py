# =====================================================================
# 📸 Frontbuffer OG 이미지 + 트윗 문구 생성기 (og_generator.py)
# =====================================================================
# 동작:
#   1. _posts/ 폴더에서 MD 파일 목록 스캔
#   2. social_output/ 에 이미 처리된 파일 스킵
#   3. 미처리 파일 → OG 이미지 PNG + 트윗 문구 txt 생성
#
# 사용법:
#   python og_generator.py              → 전체 미처리 파일 자동 처리
#   python og_generator.py --all        → 이미 처리된 것도 재생성
#   python og_generator.py --file 파일명 → 특정 파일만 처리
#
# 필요:
#   pip install pillow
# =====================================================================

import os
import re
import sys
import io
import argparse
import urllib.request
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("❌ Pillow 없음 — pip install pillow 실행하세요.")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("❌ requests 없음 — pip install requests 실행하세요.")
    sys.exit(1)

try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

# ── R2 설정 ─────────────────────────────────────────────────────────
R2_ACCOUNT_ID    = os.environ.get("R2_ACCOUNT_ID", "")
R2_ACCESS_TOKEN  = os.environ.get("R2_ACCESS_TOKEN", "")
R2_BUCKET_NAME   = "frontbuffer-images"
R2_PUBLIC_URL    = "https://images.frontbuffer.net"
UNSPLASH_KEY     = os.environ.get("UNSPLASH_ACCESS_KEY", "")

POSTS_DIR  = "_posts"
OUTPUT_DIR = "social_output"
OG_WIDTH   = 1200
OG_HEIGHT  = 630

BG_COLOR    = (26, 32, 53)
TEAL_COLOR  = (46, 196, 176)
WHITE_COLOR = (255, 255, 255)
MUTED_COLOR = (136, 153, 170)
DARK_TEAL   = (15, 42, 30)

GAMING_KEYS = ["steam", "game", "gaming", "xbox", "playstation",
               "nintendo", "fallout", "portable", "handheld", "deck"]

# Unsplash 검색 키워드 매핑 (클러스터별)
UNSPLASH_QUERY_MAP = {
    "samsung":  "samsung smartphone technology",
    "galaxy":   "samsung foldable smartphone",
    "fold":     "foldable smartphone technology",
    "chrome":   "web browser technology",
    "manifest": "web browser extension technology",
    "android":  "android smartphone technology",
    "steam":    "gaming PC hardware",
    "fallout":  "video game RPG",
    "portable": "handheld gaming device",
    "moonlight": "game streaming setup",
    "auto":     "car dashboard technology",
    "gaming":   "gaming setup hardware",
    "tech":     "technology dark minimal",
}

def get_unsplash_query(title, category):
    t = title.lower()
    for key, query in UNSPLASH_QUERY_MAP.items():
        if key in t:
            return query
    return "technology dark minimal" if category == "TECH" else "gaming setup hardware"

# 주제별 해시태그
HASHTAG_MAP = {
    "chrome":   "#Chrome #ChromeExtensions #Google #Browser #WebDev",
    "manifest": "#ChromeExtensions #ManifestV3 #Google #WebDev #Browser",
    "samsung":  "#Samsung #Android #Privacy #Tech #Smartphone",
    "android":  "#Android #Google #Privacy #Tech #Smartphone",
    "steam":    "#Steam #SteamMachine #PCGaming #Valve #Gaming",
    "gaming":   "#PCGaming #Gaming #Steam #Valve #Gamer",
    "fallout":  "#Fallout #Gaming #RPG #Bethesda #PCGaming",
    "portable": "#PortableGaming #SteamDeck #Handheld #Gaming #PCGaming",
    "default_tech":   "#Tech #Digital #Productivity #Software #Innovation",
    "default_gaming": "#Gaming #PCGaming #Steam #Gamer #VideoGames",
}

def fetch_unsplash_image(query):
    """Unsplash에서 이미지 다운로드 → PIL Image 반환."""
    if not UNSPLASH_KEY:
        return None
    try:
        url = f"https://api.unsplash.com/photos/random?query={urllib.request.quote(query)}&orientation=landscape&content_filter=high"
        req = urllib.request.Request(url, headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = __import__('json').loads(resp.read())
        img_url = data["urls"]["regular"]
        with urllib.request.urlopen(img_url, timeout=15) as resp:
            img_data = resp.read()
        return Image.open(io.BytesIO(img_data)).convert("RGB")
    except Exception as e:
        print(f"  ⚠️ Unsplash 이미지 다운로드 실패: {e}")
        return None


def upload_to_r2(local_path, r2_key):
    """R2에 파일 업로드 (requests + S3 API) → 공개 URL 반환."""
    if not R2_ACCOUNT_ID or not R2_ACCESS_TOKEN:
        return None
    try:
        # Cloudflare R2는 S3 호환 API 사용
        # API 토큰을 Bearer로 직접 사용
        endpoint = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
        url = f"{endpoint}/{R2_BUCKET_NAME}/{r2_key}"
        content_type = "image/png" if local_path.endswith(".png") else "image/jpeg"
        with open(local_path, "rb") as f:
            data = f.read()
        resp = requests.put(
            url,
            data=data,
            headers={
                "Content-Type": content_type,
                "Authorization": f"Bearer {R2_ACCESS_TOKEN}",
            },
            timeout=30,
        )
        if resp.status_code in (200, 204):
            return f"{R2_PUBLIC_URL}/{r2_key}"
        else:
            print(f"  ⚠️ R2 업로드 실패 ({resp.status_code}): {resp.text[:100]}")
            return None
    except Exception as e:
        print(f"  ⚠️ R2 업로드 실패: {e}")
        return None


def get_hashtags(title, category):
    t = title.lower()
    for key in ["manifest", "chrome", "samsung", "android", "fallout", "portable", "steam"]:
        if key in t:
            return HASHTAG_MAP[key]
    if "gaming" in t or category == "GAMING":
        return HASHTAG_MAP["default_gaming"]
    return HASHTAG_MAP["default_tech"]


def get_hook(title, excerpt, category):
    """글 제목/내용 기반으로 트윗 후킹 문장 1줄 생성 — 글별 고유 문장."""
    t = title.lower()

    # Chrome / Manifest — 글별로 다른 문장
    if "deprecation" in t and ("complete guide" in t or "hub" in t):
        return "Google's Chrome extension deadline is August 31. Here's the full picture — what broke, why, and what to do next."
    if "how to check" in t and "manifest" in t:
        return "Not sure which of your Chrome extensions will survive August 31? Here's exactly how to check in 30 seconds."
    if "alternatives" in t and "manifest" in t:
        return "Your go-to Chrome extensions are going away. These are the replacements that actually hold up under Manifest V3."
    if "what is" in t and ("manifest v3" in t or "extensions break" in t):
        return "Millions of Chrome users lost extensions without warning. Here's the actual reason — and it's not going away."

    # Samsung Health
    if "samsung health" in t and "backup" in t:
        return "Switching phones or deleting your Samsung account? Don't lose years of health data first."
    if "samsung health" in t and ("google" in t or "comparison" in t):
        return "Samsung Health vs Google Health Connect — we broke down exactly which one handles your data better."

    # Steam Machine
    if "steam machine" in t and "overheating" in t:
        return "The red light on your Steam Machine isn't what you think. Valve confirmed it's a BIOS bug — not a hardware failure."
    if "steam machine" in t and "led" in t:
        return "Every Steam Machine LED color means something different. Here's what each warning light actually tells you."

    # Android / Privacy
    if "secure folder" in t or "safe folder" in t:
        return "Samsung Secure Folder vs Google Files Safe Folder — one uses Knox hardware encryption. The other doesn't."

    # fallback — excerpt 활용 (보일러플레이트 제거)
    clean = excerpt
    for pattern in [
        r"In an increasingly digital world[^.]*\.",
        r"As technology continues[^.]*\.",
        r"In today's (rapidly|fast)[^.]*\.",
        r"With the rise of[^.]*\.",
    ]:
        clean = re.sub(pattern, "", clean).strip()
    if clean and len(clean) > 20:
        return clean[:140].rsplit(" ", 1)[0] + ("…" if len(clean) > 140 else "")
    return f"New on Frontbuffer: {title}"


def get_font(size, bold=False):
    font_paths = []
    if sys.platform == "win32":
        win = os.environ.get("WINDIR", "C:\\Windows")
        font_paths = [
            os.path.join(win, "Fonts", "arialbd.ttf" if bold else "arial.ttf"),
            os.path.join(win, "Fonts", "segoeui.ttf"),
        ]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def parse_md(filepath):
    text = Path(filepath).read_text(encoding="utf-8")
    title = ""
    category = "TECH"
    excerpt = ""

    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        t = re.search(r"^title:\s*['\"]?(.+?)['\"]?\s*$", fm, re.MULTILINE)
        if t:
            title = t.group(1).strip().strip("'\"")
        e = re.search(r"^excerpt:\s*['\"]?(.+?)['\"]?\s*$", fm, re.MULTILINE)
        if e:
            excerpt = e.group(1).strip().strip("'\"")
        c = re.search(r"^categories:\s*\[(.+?)\]", fm, re.MULTILINE)
        if c:
            cats = c.group(1).lower()
            category = "GAMING" if "gaming" in cats else "TECH"

    if not title:
        h1 = re.search(r"^# (.+)$", text, re.MULTILINE)
        if h1:
            title = h1.group(1).strip()

    if not excerpt:
        body = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)
        body = re.sub(r"^#.+$", "", body, flags=re.MULTILINE)
        body = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", body)
        lines = [l.strip() for l in body.splitlines() if l.strip()]
        if lines:
            raw = lines[0]
            excerpt = raw[:120].rsplit(" ", 1)[0] + "…" if len(raw) > 120 else raw

    if any(k in title.lower() for k in GAMING_KEYS):
        category = "GAMING"

    return title, category, excerpt


def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
        if len(lines) == 2:
            current = current[:40] + "…"
            break
    if current and len(lines) < 3:
        lines.append(current)
    return lines[:2]


def draw_rounded_rect(draw, xy, radius, fill, outline=None, outline_width=2):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.ellipse([x1, y1, x1 + radius*2, y1 + radius*2], fill=fill)
    draw.ellipse([x2 - radius*2, y1, x2, y1 + radius*2], fill=fill)
    draw.ellipse([x1, y2 - radius*2, x1 + radius*2, y2], fill=fill)
    draw.ellipse([x2 - radius*2, y2 - radius*2, x2, y2], fill=fill)
    if outline:
        draw.rectangle([x1 + radius, y1, x2 - radius, y1 + outline_width], fill=outline)
        draw.rectangle([x1 + radius, y2 - outline_width, x2 - radius, y2], fill=outline)
        draw.rectangle([x1, y1 + radius, x1 + outline_width, y2 - radius], fill=outline)
        draw.rectangle([x2 - outline_width, y1 + radius, x2, y2 - radius], fill=outline)


def generate_og_image(title, category, excerpt, out_path, unsplash_img=None):
    # 제목 길이에 따라 폰트 크기 자동 조정
    title_font_size = 54 if len(title) <= 40 else (44 if len(title) <= 60 else 36)

    # ── 배경 생성 ──────────────────────────────────────────────────
    if unsplash_img is not None:
        # Unsplash 이미지를 배경으로 사용
        bg = unsplash_img.resize((OG_WIDTH, OG_HEIGHT), Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=3))
        # 어두운 오버레이 (텍스트 가독성 확보)
        overlay = Image.new("RGBA", (OG_WIDTH, OG_HEIGHT), (20, 26, 45, 200))
        img = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    else:
        img = Image.new("RGB", (OG_WIDTH, OG_HEIGHT), BG_COLOR)

    draw = ImageDraw.Draw(img, "RGBA")

    # 그리드 라인 (Unsplash 배경 있을 때는 더 투명하게)
    grid_alpha = 5 if unsplash_img else 10
    for y in [157, 315, 472]:
        draw.line([(0, y), (OG_WIDTH, y)], fill=(255, 255, 255, grid_alpha), width=1)
    for x in [300, 600, 900]:
        draw.line([(x, 0), (x, OG_HEIGHT)], fill=(255, 255, 255, grid_alpha), width=1)

    cx, cy = 1050, 315
    for r, alpha in [(320, 25), (220, 20), (120, 15)]:
        overlay_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay_img)
        ov_draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(*TEAL_COLOR, alpha), width=1)
        img.paste(Image.alpha_composite(img.convert("RGBA"), overlay_img).convert("RGB"))
        draw = ImageDraw.Draw(img, "RGBA")

    font_brand   = get_font(28, bold=True)
    font_label   = get_font(15)
    font_title   = get_font(title_font_size, bold=True)
    font_excerpt = get_font(22)
    font_badge   = get_font(14, bold=True)
    font_domain  = get_font(18)

    draw.text((80, 55), "FRONTBUFFER", font=font_brand, fill=TEAL_COLOR)
    draw.text((83, 92), "EDITORIAL", font=font_label, fill=MUTED_COLOR)
    draw.line([(80, 130), (500, 130)], fill=(*TEAL_COLOR, 80), width=1)

    title_lines = wrap_text(title, font_title, 900, draw)
    ty = 175
    for line in title_lines:
        draw.text((80, ty), line, font=font_title, fill=WHITE_COLOR)
        ty += title_font_size + 14

    excerpt_lines = wrap_text(excerpt, font_excerpt, 950, draw)
    ty += 20
    for line in excerpt_lines:
        draw.text((80, ty), line, font=font_excerpt, fill=MUTED_COLOR)
        ty += 34

    badge_bg = DARK_TEAL if category == "GAMING" else (10, 26, 46)
    draw_rounded_rect(draw, [80, 555, 200, 595], radius=6, fill=badge_bg, outline=TEAL_COLOR)
    bbox = draw.textbbox((0, 0), category, font=font_badge)
    bw = bbox[2] - bbox[0]
    draw.text((140 - bw // 2, 568), category, font=font_badge, fill=TEAL_COLOR)

    domain = "frontbuffer.net"
    bbox = draw.textbbox((0, 0), domain, font=font_domain)
    dw = bbox[2] - bbox[0]
    draw.text((OG_WIDTH - 80 - dw, 578), domain, font=font_domain, fill=(*TEAL_COLOR, 130))

    img.save(out_path, "PNG")


def generate_tweet(title, category, excerpt, url_slug):
    cat_path = "gaming" if category == "GAMING" else "tech"
    url      = f"https://frontbuffer.net/{cat_path}/{url_slug}/"
    hook     = get_hook(title, excerpt, category)
    hashtags = get_hashtags(title, category)

    return f"""{hook}

{url}

{hashtags}"""


def process_file(md_path, force=False):
    stem     = Path(md_path).stem
    url_slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
    slug_dir = os.path.join(OUTPUT_DIR, url_slug)
    out_png  = os.path.join(slug_dir, "og.png")
    out_tweet= os.path.join(slug_dir, "tweet.txt")

    if not force and os.path.exists(out_png) and os.path.exists(out_tweet):
        print(f"  ✅ 스킵: {url_slug}")
        return False

    print(f"  🆕 처리 중: {url_slug}")
    title, category, excerpt = parse_md(md_path)
    if not title:
        print(f"  ⚠️ 제목 추출 실패 — 스킵")
        return False

    print(f"     제목: {title[:55]}...")
    os.makedirs(slug_dir, exist_ok=True)

    # ── Unsplash 이미지 가져오기 ──────────────────────────────────
    unsplash_img = None
    header_image_url = None
    if UNSPLASH_KEY:
        query = get_unsplash_query(title, category)
        print(f"     🔍 Unsplash 검색: {query}")
        unsplash_img = fetch_unsplash_image(query)
        if unsplash_img:
            print(f"     ✅ Unsplash 이미지 다운로드 완료")

    # ── OG 이미지 생성 ────────────────────────────────────────────
    generate_og_image(title, category, excerpt, out_png, unsplash_img=unsplash_img)

    # ── R2에 header 이미지 업로드 ─────────────────────────────────
    if unsplash_img and HAS_BOTO3 and R2_ACCOUNT_ID:
        # header 이미지 저장 (1200x630, 약간 blur 적용)
        header_path = os.path.join(slug_dir, "header.jpg")
        header_img = unsplash_img.resize((1200, 630), Image.LANCZOS)
        header_img.save(header_path, "JPEG", quality=85)
        r2_key = f"posts/{url_slug}/header.jpg"
        header_image_url = upload_to_r2(header_path, r2_key)
        if header_image_url:
            print(f"     ☁️ R2 업로드 완료: {header_image_url}")

    # ── OG 이미지 R2 업로드 ───────────────────────────────────────
    if HAS_BOTO3 and R2_ACCOUNT_ID:
        r2_og_key = f"posts/{url_slug}/og.png"
        og_url = upload_to_r2(out_png, r2_og_key)
        if og_url:
            print(f"     ☁️ OG 이미지 R2 업로드: {og_url}")

    # ── _posts/ 파일에 header.image frontmatter 추가 ─────────────
    if header_image_url:
        md_text = Path(md_path).read_text(encoding="utf-8")
        if "header:" not in md_text:
            header_block = (
                "header:\n"
                f"  image: {header_image_url}\n"
                "  overlay_filter: 0.5\n"
            )
            md_text = md_text.replace(
                "author_profile: false",
                f"{header_block}author_profile: false"
            )
            Path(md_path).write_text(md_text, encoding="utf-8")
            print(f"     📝 header.image frontmatter 추가됨")

    tweet = generate_tweet(title, category, excerpt, url_slug)
    Path(out_tweet).write_text(tweet, encoding="utf-8")

    print(f"     📸 {out_png}")
    print(f"     📝 {out_tweet}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all",  action="store_true")
    parser.add_argument("--file", default="")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"📸 Frontbuffer OG 생성기")
    print(f"{'='*60}")

    if not os.path.exists(POSTS_DIR):
        print(f"❌ '{POSTS_DIR}' 폴더 없음")
        sys.exit(1)

    if args.file:
        target = args.file if args.file.endswith(".md") else args.file + ".md"
        target = os.path.join(POSTS_DIR, os.path.basename(target))
        if not os.path.exists(target):
            print(f"❌ 파일 없음: {target}")
            sys.exit(1)
        process_file(target, force=True)
        return

    md_files = sorted(Path(POSTS_DIR).glob("*.md"))
    if not md_files:
        print(f"❌ '{POSTS_DIR}' 에 MD 파일 없음")
        sys.exit(1)

    print(f"  _posts/ 파일: {len(md_files)}개\n")
    processed = skipped = 0
    for md in md_files:
        if process_file(str(md), force=args.all):
            processed += 1
        else:
            skipped += 1

    print(f"\n{'='*60}")
    print(f"✅ 완료: 신규 {processed}개 / 스킵 {skipped}개")
    print(f"   결과물: {OUTPUT_DIR}/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
