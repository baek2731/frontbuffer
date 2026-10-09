#!/usr/bin/env python3
# =====================================================================
# ✂️ excerpt(메타 설명) 일괄 정리 (fix_excerpts.py)
# =====================================================================
# 대상 (아래 중 하나라도 해당하는 글만 수정):
#   - excerpt 가 "…" 로 잘린 글
#   - 170자 초과 (검색 결과에서 잘림)
#   - 110자 미만 (너무 짧음)
#   - 마크다운 기호(*, `, [ ]) 포함
#
# 방식:
#   - 잘린 글: 본문 첫 문단에서 문장 단위로 155자 이내를 다시 만든다.
#   - 긴 글: 기존 excerpt 를 문장 단위로 줄인다.
#   - 결과는 항상 작은따옴표 YAML 로 쓰고, "..." 로 끝나지 않게 한다.
#
# 사용법 (저장소 루트에서):
#   python fix_excerpts.py           ← 미리보기 (파일 수정 없음, 전/후 출력)
#   python fix_excerpts.py --apply   ← excerpt 줄만 수정
#
# 적용 후 마지막에 출력되는 날짜 목록으로 OG 이미지를 재생성하세요
# (excerpt 가 이미지에 들어갑니다).
# =====================================================================

import re
import sys
from pathlib import Path

POSTS = Path("_posts")
LIMIT = 155
TRAILING_WORDS = {"and", "or", "the", "a", "an", "of", "to", "in", "on", "for", "with",
                  "by", "from", "as", "at", "that", "which", "is", "are", "was", "were",
                  "when", "where", "how", "what", "why", "whether", "than", "then", "but",
                  "if", "because", "while", "although", "between", "including", "into",
                  "about", "your", "you", "it", "its", "this", "these", "those", "also"}


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        v = v[1:-1]
        v = v.replace("''", "'")
    return v


def clean(text):
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*`#>]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def cut_clause(text, limit=LIMIT):
    """한 문장이 limit 보다 길 때: 쉼표/대시 경계 → 단어 경계 순으로 자르고 마침표로 끝낸다."""
    if len(text) <= limit:
        return text
    head = text[:limit]
    best = max(head.rfind(", "), head.rfind(" — "), head.rfind(" - "), head.rfind("; "))
    if best >= max(25, int(len(head) * 0.5)):
        out = head[:best]
    else:
        out = head.rsplit(" ", 1)[0]
    words = out.split()
    while words and words[-1].lower().strip(",.;:") in TRAILING_WORDS:
        words.pop()
    out = " ".join(words).rstrip(" ,;:-—")
    return out + "."


def sentences_to_limit(text, limit=LIMIT, min_fill=125):
    """문장 단위로 limit 이내까지 채우고, 너무 짧으면 다음 문장의 앞부분을 이어 붙인다."""
    sents = re.split(r"(?<=[.!?])\s+", text)
    out, used = "", 0
    for s in sents:
        cand = (out + " " + s).strip()
        if len(cand) <= limit:
            out, used = cand, used + 1
        else:
            break
    if len(out) < min_fill and used < len(sents):
        room = limit - len(out) - 1
        if room >= 35:
            part = cut_clause(sents[used], room)
            if len(part) >= 30:
                out = (out + " " + part).strip()
    return out


def body_paragraph(body):
    """본문에서 첫 '문단'(제목/표/목록/구분선 제외)을 가져온다."""
    paras, cur = [], []
    for line in body.splitlines():
        s = line.strip()
        if not s:
            if cur:
                paras.append(" ".join(cur)); cur = []
            continue
        if s.startswith(("#", "|", "-", "*", ">", "!", "---", "1.", "{%")) or s.startswith("*Checked"):
            if cur:
                paras.append(" ".join(cur)); cur = []
            continue
        cur.append(s)
    if cur:
        paras.append(" ".join(cur))
    for p in paras:
        p = clean(p)
        if len(p) >= 60:
            return p
    return ""


def make_new(old, body):
    old_clean = clean(old)
    truncated = old.rstrip().endswith(("…", "..."))
    if truncated:
        base = body_paragraph(body) or re.sub(r"[…\.]+$", "", old_clean)
    else:
        base = old_clean
    new = sentences_to_limit(base)
    if len(new) < 60:
        new = cut_clause(base)
    return new


def needs_fix(ex):
    return (ex.rstrip().endswith(("…", "..."))
            or len(ex) > 170 or len(ex) < 110
            or re.search(r"[*`\[\]]", ex) is not None)


def main():
    apply = "--apply" in sys.argv
    changed, dates, skipped = 0, [], []
    for p in sorted(POSTS.glob("*.md")):
        with open(p, encoding="utf-8", newline="") as fh:
            text = fh.read()
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        fm, body = text[:end], text[end + 4:]
        m = re.search(r"^excerpt:[ \t]*(.*?)(\r?)$", fm, re.M)
        if not m:
            continue
        raw = m.group(1)
        if raw.startswith((">", "|")) or raw == "":
            skipped.append(p.name)
            continue
        old = unquote(raw)
        if not needs_fix(old):
            continue
        new = make_new(old, body)
        if not new or new == old:
            continue
        print(f"\n{'수정' if apply else '대상'}: {p.name}")
        print(f"   전 ({len(old):>3}자): {old[:110]}{'…' if len(old) > 110 else ''}")
        print(f"   후 ({len(new):>3}자): {new}")
        changed += 1
        dm = re.match(r"^(\d{4}-\d{2}-\d{2})", p.name)
        if dm and dm.group(1) not in dates:
            dates.append(dm.group(1))
        if apply:
            yaml_val = "'" + new.replace("'", "''") + "'"
            fm2 = fm[:m.start()] + "excerpt: " + yaml_val + m.group(2) + fm[m.end():]
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(fm2 + text[end:])
    print(f"\n{'적용' if apply else '대상'}: {changed}개 글")
    if skipped:
        print(f"건너뜀(여러 줄 excerpt): {skipped}")
    if dates:
        print("\nOG 재생성 날짜(Actions → OG Image Regenerate → date 칸에 붙여넣기):")
        print(" ".join(sorted(dates)))
    if not apply and changed:
        print("\n결과가 괜찮으면: python fix_excerpts.py --apply")


if __name__ == "__main__":
    main()
