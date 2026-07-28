import json, datetime

pipe = json.load(open('content_pipeline.json', encoding='utf-8'))

targets = [
    ('2026-W29', 'Android Ecosystem', 'GUIDE'),
    ('2026-W30', 'Google Android Ecosystem', 'GUIDE'),
]

for week, name, ct in targets:
    for s in pipe.get('weekly_selections', {}).get(week, []):
        if s.get('cluster_name') == name and s.get('content_type') == ct and s.get('status') == 'candidate':
            s['status'] = 'writing'
            print(f'마킹: {week} {name} {ct}')

pipe['_last_updated'] = datetime.datetime.utcnow().isoformat()
json.dump(pipe, open('content_pipeline.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('완료')
