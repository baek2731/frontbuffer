#!/usr/bin/env python3
# =====================================================================
# 🖼️ 헤더 이미지 경로 정리 (fix_headers.py)
# =====================================================================
# 문제: 글의 front matter header.image 가 가리키는 폴더 이름이 파일명과 다르면
#       (예: 파일명 ...-a-comprehensive-comparis ↔ 이미지 ...-a-full-comparis)
#       OG 이미지를 재생성해도 사이트는 옛 이미지를 계속 보여준다.
#       og_generator.py 는 항상 "파일명에서 날짜를 뺀 이름" 폴더에 이미지를 올린다.
#
# 사용법 (저장소 루트에서):
#   python fix_headers.py           ← 미리보기 (파일 수정 없음)
#   python fix_headers.py --apply   ← header.image 줄만 수정
# =====================================================================

import re
import sys
from pathlib import Path

POSTS = Path("_posts")


def main():
    apply = "--apply" in sys.argv
    changed = 0
    for p in sorted(POSTS.glob("*.md")):
        m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$", p.name)
        if not m:
            continue
        slug = m.group(1)                      # og_generator 와 같은 규칙 (끝의 '-' 유지)
        with open(p, encoding="utf-8", newline="") as fh:
            text = fh.read()
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        block, rest = text[:end], text[end:]
        lines = block.split("\n")
        in_header = False
        new_lines, hit = [], False
        for line in lines:
            if re.match(r"^header:\s*\r?$", line):
                in_header = True
            elif in_header and line and not line.startswith((" ", "\t")):
                in_header = False
            mm = re.match(r"^(\s+image:\s*)(\S+?)(\r?)$", line) if in_header else None
            if mm:
                url = mm.group(2)
                sm = re.search(r"/posts/([^/]+)/", url)
                if sm and sm.group(1) != slug:
                    new_url = url.replace(f"/posts/{sm.group(1)}/", f"/posts/{slug}/", 1)
                    print(f"{'수정' if apply else '대상'}: {p.name}")
                    print(f"      {sm.group(1)}  →  {slug}")
                    line = f"{mm.group(1)}{new_url}{mm.group(3)}"
                    hit = True
            new_lines.append(line)
        if hit:
            changed += 1
            if apply:
                with open(p, "w", encoding="utf-8", newline="") as fh:
                    fh.write("\n".join(new_lines) + rest)
    print(f"\n{'적용' if apply else '대상'} {changed}개 글")
    if not apply and changed:
        print("실제로 바꾸려면: python fix_headers.py --apply")


if __name__ == "__main__":
    main()
