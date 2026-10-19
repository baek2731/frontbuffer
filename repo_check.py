#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""repo_check.py - 공개 GitHub 저장소에 올라가면 안 되는 것을 점검합니다 (읽기 전용, 파일을 바꾸지 않음).

사용법 (저장소 루트에서):
    python repo_check.py              추적 중인 파일 점검
    python repo_check.py --history    과거 커밋 기록의 비밀값 패턴까지 검색 (느릴 수 있음)
    python repo_check.py --list-served   사이트에 그대로 공개되는 파일 전체 목록만 출력

점검 항목
  1. 비밀값 패턴 (API 키, 토큰, 웹훅 주소, 개인 키)
  2. 개인정보 (이메일, 내 PC 경로)
  3. 올리지 않는 게 좋은 파일 (생성물, 백업, .env 등)
  4. 사이트에 그대로 공개되는 파일 (Jekyll 이 정적 파일로 복사하는 것)
  5. .gitignore 에 걸리는데 이미 추적 중인 파일
  6. 큰 파일
Python 3.10 호환.
"""
import fnmatch
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SECRET_PATTERNS = [
    ("Google API 키", re.compile(r"(?<![A-Za-z0-9_\-])AIza[0-9A-Za-z_\-]{35}(?![A-Za-z0-9_\-])")),
    ("GitHub 토큰", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),
    ("GitHub PAT", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("Discord 웹훅", re.compile(r"https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/\d+/[\w\-]+")),
    ("개인 키(PEM)", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS 액세스 키", re.compile(r"(?<![A-Za-z0-9+/=])AKIA[0-9A-Z]{16}(?![A-Za-z0-9+/=])")),
    ("Slack 토큰", re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("Anthropic 키", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI 형식 키", re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9]{32,}(?![A-Za-z0-9])")),
    ("R2/S3 엔드포인트(계정 ID)", re.compile(r"[0-9a-f]{32}\.r2\.cloudflarestorage\.com")),
    ("키=값 형태", re.compile(
        r"(?i)(api[_\-]?key|secret|token|passwd|password|access[_\-]?key)\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{16,}['\"]")),
]
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
EMAIL_IGNORE = ("noreply", "example.com", "users.noreply.github.com", "@2x", "@3x")
PATH_RE = re.compile(r"[A-Za-z]:\\Users\\[^\\\s\"']+")

UNWANTED_NAMES = {
    "audit_report.txt", "git_inventory.csv", "content_audit.csv", "content_audit.md",
    "site_report.txt", "search_console_urls.txt", ".env", "thumbs.db", ".ds_store",
}
UNWANTED_SUFFIXES = (".bak", ".pyc", ".log", ".tmp", ".swp", ".pem", ".key", ".pfx", ".p12")
BIG_BYTES = 5 * 1024 * 1024
TEXT_MAX_BYTES = 2 * 1024 * 1024
LIB_PATH_MARKERS = ("site-packages/", "venv/", "node_modules/", ".venv/")
SERVED_EXT_NOTE = (".py", ".csv", ".json", ".txt", ".md", ".yml", ".yaml", ".bak", ".log", ".sh", ".bat", ".ps1")


def run(args):
    p = subprocess.run(["git", "-c", "core.quotepath=off"] + args, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", errors="replace"), p.stderr.decode("utf-8", errors="replace")


def mask(s):
    if len(s) <= 8:
        return "*" * len(s)
    return s[:4] + "..." + "(%d자)" % len(s)


def tracked_files():
    code, out, err = run(["ls-files", "-z"])
    if code != 0:
        print("git 저장소가 아니거나 git 실행 실패:", err.strip())
        sys.exit(1)
    return [x for x in out.split("\0") if x]


def read_text(path):
    try:
        if os.path.getsize(path) > TEXT_MAX_BYTES:
            return None
        with open(path, "rb") as f:
            data = f.read()
        if b"\0" in data[:4096]:
            return None
        return data.decode("utf-8", errors="ignore")
    except OSError:
        return None


def parse_excludes(config_text):
    """_config.yml 의 exclude: 목록을 단순 파싱합니다."""
    items = []
    if not config_text:
        return items
    lines = config_text.splitlines()
    inside = False
    for ln in lines:
        s = ln.rstrip()
        if re.match(r"^exclude\s*:", s):
            inside = True
            rest = s.split(":", 1)[1].strip()
            if rest.startswith("["):
                items += [x.strip().strip("'\"") for x in rest.strip("[]").split(",") if x.strip()]
                inside = False
            continue
        if inside:
            m = re.match(r"^\s*-\s*(.+?)\s*(#.*)?$", s)
            if m:
                items.append(m.group(1).strip().strip("'\""))
            elif s.strip() == "" or s.strip().startswith("#"):
                continue
            else:
                inside = False
    return items


def jekyll_default_excluded(path):
    parts = path.replace("\\", "/").split("/")
    for part in parts:
        if part.startswith("_") or part.startswith(".") or part.startswith("#") or part.endswith("~"):
            return True
    top = parts[0]
    if top in ("node_modules", "vendor", "Gemfile", "Gemfile.lock", "gemfiles"):
        return True
    return False


def excluded_by_config(path, excludes):
    p = path.replace("\\", "/")
    base = p.split("/")[-1]
    for e in excludes:
        e2 = e.replace("\\", "/").strip("/")
        if not e2:
            continue
        if p == e2 or p.startswith(e2 + "/"):
            return True
        if fnmatch.fnmatch(p, e2) or fnmatch.fnmatch(base, e2):
            return True
    return False


def has_front_matter(path):
    try:
        with open(path, "rb") as f:
            head = f.read(4)
        return head.startswith(b"---") or head.startswith(b"\xef\xbb\xbf---")
    except OSError:
        return False


def section(title):
    print("")
    print("=" * 60)
    print(title)
    print("=" * 60)


def list_served(files):
    config_text = None
    if os.path.exists("_config.yml"):
        with open("_config.yml", "rb") as cf:
            config_text = cf.read().decode("utf-8", errors="ignore")
    excludes = parse_excludes(config_text)
    print("# _config.yml exclude: %s" % (", ".join(excludes) if excludes else "(없음)"))
    n = 0
    for f in files:
        if jekyll_default_excluded(f) or excluded_by_config(f, excludes):
            continue
        norm = f.replace("\\", "/")
        if norm.split("/")[0] == "assets":
            continue
        if os.path.splitext(f)[1].lower() in SERVED_EXT_NOTE:
            print(norm)
            n += 1
    print("# 합계 %d개" % n)


def main():
    history = "--history" in sys.argv
    files = tracked_files()
    if "--list-served" in sys.argv:
        list_served(files)
        return
    print("추적 중인 파일: %d개" % len(files))

    danger = 0
    warn = 0

    # 1, 2. 비밀값 / 개인정보
    section("1. 비밀값 패턴 (발견되면 [위험])")
    secret_hits = []
    emails = {}
    paths_hits = []
    for f in files:
        text = read_text(f)
        if text is None:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for name, rx in SECRET_PATTERNS:
                for m in rx.finditer(line):
                    secret_hits.append((f, i, name, mask(m.group(0))))
            for m in EMAIL_RE.finditer(line):
                addr = m.group(0)
                if not any(x in addr.lower() for x in EMAIL_IGNORE):
                    emails.setdefault(addr, []).append(f)
            m2 = PATH_RE.search(line)
            if m2:
                paths_hits.append((f, i, m2.group(0)))
    if secret_hits:
        for f, i, name, masked in secret_hits[:60]:
            print("[위험] %s:%d  %s  %s" % (f, i, name, masked))
        if len(secret_hits) > 60:
            print("... 외 %d건" % (len(secret_hits) - 60))
        danger += len(secret_hits)
        print("")
        print("조치: 해당 키는 이미 공개된 것으로 보고 즉시 폐기(재발급)하세요. 파일에서 지우는 것만으로는 부족합니다.")
    else:
        print("발견 없음 (정규식으로 찾을 수 있는 범위 안에서)")

    section("2. 개인정보 (참고용)")
    if emails:
        for addr, fl in sorted(emails.items()):
            uniq = sorted(set(fl))
            print("[주의] 이메일 %s  <- %s%s" % (addr, ", ".join(uniq[:3]), " 외" if len(uniq) > 3 else ""))
            warn += 1
    else:
        print("이메일 주소: 없음")
    if paths_hits:
        for f, i, p in paths_hits[:20]:
            print("[참고] 내 PC 경로 %s:%d  %s" % (f, i, p))
        if len(paths_hits) > 20:
            print("... 외 %d건" % (len(paths_hits) - 20))
        print("(스크립트·문서 안의 PC 경로는 보안 위험은 작지만 사용자 이름이 노출됩니다)")
    else:
        print("PC 경로(C:\\Users\\...): 없음")

    # 3. 올리지 않는 게 좋은 파일
    section("3. 올리지 않는 게 좋은 파일")
    unwanted = []
    for f in files:
        low = f.replace("\\", "/").lower()
        base = low.split("/")[-1]
        if base in UNWANTED_NAMES or low.endswith(UNWANTED_SUFFIXES) or "__pycache__/" in low:
            unwanted.append(f)
    if unwanted:
        for f in unwanted[:50]:
            print("[주의] %s" % f)
        warn += len(unwanted)
        print("조치(로컬 파일은 지우지 않고 추적만 해제): git rm --cached 파일이름  → 커밋 → 푸시, 그리고 .gitignore 에 추가")
    else:
        print("해당 없음")

    # 4. 사이트에 그대로 공개되는 파일
    section("4. 사이트(frontbuffer.net)에 그대로 공개되는 파일 추정")
    config_text = None
    if os.path.exists("_config.yml"):
        with open("_config.yml", "rb") as cf:
            config_text = cf.read().decode("utf-8", errors="ignore")
    excludes = parse_excludes(config_text)
    if config_text is None:
        print("[주의] _config.yml 을 찾지 못했습니다. 저장소 루트에서 실행했는지 확인하세요.")
    else:
        print("_config.yml exclude 항목: %s" % (", ".join(excludes) if excludes else "(없음)"))
    served = []
    for f in files:
        if jekyll_default_excluded(f):
            continue
        if excluded_by_config(f, excludes):
            continue
        served.append(f)
    notes = []
    for f in served:
        ext = os.path.splitext(f)[1].lower()
        top = f.replace("\\", "/").split("/")[0]
        if ext in SERVED_EXT_NOTE and "/" in f.replace("\\", "/") and top not in ("assets",):
            notes.append(f)
        elif ext in SERVED_EXT_NOTE and "/" not in f.replace("\\", "/"):
            notes.append(f)
    # 폴더별 집계
    by_top = {}
    for f in notes:
        top = f.replace("\\", "/").split("/")[0] if "/" in f.replace("\\", "/") else "(루트)"
        by_top.setdefault(top, []).append(f)
    if by_top:
        for top in sorted(by_top):
            fl = by_top[top]
            fm = len([x for x in fl if has_front_matter(x)])
            print("[주의] %s : %d개 (front matter 있어 페이지로 렌더링 %d개 / 나머지는 원본 파일 그대로 공개)" % (top, len(fl), fm))
            for x in fl[:4]:
                print("        예) %s" % x)
        warn += len(by_top)
        print("")
        print("조치: 공개할 필요가 없으면 _config.yml 의 exclude: 에 폴더/파일을 추가하세요.")
        print("      (예: research_data, *.py, content_audit.csv) — 이미 색인된 주소는 Search Console 에서 삭제 요청")
    else:
        print("해당 없음 (추정)")
    need = ["research_data"]
    missing = [n for n in need if n not in [e.strip("/") for e in excludes]]
    if config_text is not None and missing:
        print("[위험] _config.yml exclude 에 없음: %s" % ", ".join(missing))
        danger += 1

    # 5. .gitignore 에 걸리는 추적 파일
    section("5. .gitignore 에 걸리는데 이미 추적 중인 파일")
    code, out, err = run(["ls-files", "-ci", "--exclude-standard"])
    ign = [x for x in out.splitlines() if x.strip()]
    if ign:
        for x in ign[:30]:
            print("[주의] %s" % x)
        warn += len(ign)
        print("조치: git rm --cached 파일이름")
    else:
        print("해당 없음")

    # 6. 큰 파일
    section("6. 큰 파일 (5MB 이상)")
    big = []
    for f in files:
        try:
            if os.path.getsize(f) >= BIG_BYTES:
                big.append((f, os.path.getsize(f)))
        except OSError:
            pass
    if big:
        for f, sz in big:
            print("[주의] %s  %.1fMB" % (f, sz / 1024.0 / 1024.0))
        warn += len(big)
    else:
        print("해당 없음")

    # 7. 과거 기록
    if history:
        section("7. 과거 커밋 기록의 비밀값 패턴")
        high = [x for x in SECRET_PATTERNS if x[0] != "키=값 형태"]
        p = subprocess.Popen(["git", "-c", "core.quotepath=off", "log", "--all", "-p", "-U0", "--no-color",
                              "--format=COMMIT:%h %s"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        commit = ""
        cur_file = ""
        found = {}
        for raw in p.stdout:
            line = raw.decode("utf-8", errors="ignore").rstrip("\n")
            if line.startswith("COMMIT:"):
                commit = line[7:]
                continue
            if line.startswith("+++ b/"):
                cur_file = line[6:]
                continue
            if any(mk in cur_file.replace("\\", "/") for mk in LIB_PATH_MARKERS):
                continue
            if not line.startswith("+") or line.startswith("+++"):
                continue
            for name, rx in high:
                m = rx.search(line)
                if m:
                    key = (commit.split(" ")[0], cur_file, name)
                    if key not in found:
                        found[key] = mask(m.group(0))
        p.wait()
        if found:
            for (c, f, name), mk in list(found.items())[:60]:
                print("[위험] 커밋 %s  %s  %s  %s" % (c, f, name, mk))
            danger += len(found)
            print("조치: 공개 저장소에 한 번이라도 올라간 키는 폐기(재발급)가 원칙입니다. 기록 삭제는 그다음 문제입니다.")
        else:
            print("발견 없음")

    section("요약")
    print("[위험] %d건 / [주의] %d건" % (danger, warn))
    print("정규식으로 찾는 방식이라 모든 비밀값을 보장하지 못합니다. 의심되면 해당 서비스에서 키를 재발급하세요.")


if __name__ == "__main__":
    main()
