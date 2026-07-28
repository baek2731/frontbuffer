import json
import datetime

pipe = json.load(open('content_pipeline.json', encoding='utf-8'))

for s in pipe.get('weekly_selections', {}).get('2026-W29', []):
    if s.get('cluster_name') == 'Portable Gaming' and s.get('status') == 'candidate':
        s['status'] = 'writing'
        print(f'마킹: {s["content_type"]}')

pipe['_last_updated'] = datetime.datetime.utcnow().isoformat()
json.dump(pipe, open('content_pipeline.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('완료')
