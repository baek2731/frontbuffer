import re
from pathlib import Path

posts_dir = '_posts/'
files = sorted(Path(posts_dir).glob('*.md'))
changed = 0
for f in files:
    content = f.read_text(encoding='utf-8')
    new_content = re.sub(
        r'(header:\s*\n\s*image: https://images\.frontbuffer\.net/posts/[^/]+/)header\.jpg(\s*\n\s*overlay_filter:) 0\.5',
        r'\1og.png\g<2> 0',
        content
    )
    if new_content != content:
        f.write_text(new_content, encoding='utf-8')
        changed += 1
        print(f'OK: {f.name}')
print(f'총 {changed}개 변경')
