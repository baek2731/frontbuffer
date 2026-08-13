import json, datetime

pipe = json.load(open('content_pipeline.json', encoding='utf-8'))
hubs = pipe.get('hub_clusters', {})

# Steam Machine
hubs['Steam Machine']['spoke_urls']['Steam Machine Hardware Management (GUIDE)'] = \
    'https://frontbuffer.net/gaming/how-to-troubleshoot-steam-machine-overheating-and-red-light-issues/'
hubs['Steam Machine']['spoke_urls']['Steam Machine Hardware Management (COMPARISON)'] = \
    'https://frontbuffer.net/gaming/steam-machine-led-error-codes-what-each-warning-light-actually-means/'
hubs['Steam Machine']['internal_links'] = [
    'https://frontbuffer.net/gaming/how-to-troubleshoot-steam-machine-overheating-and-red-light-issues/',
    'https://frontbuffer.net/gaming/steam-machine-led-error-codes-what-each-warning-light-actually-means/',
    'PENDING'
]
print('✅ Steam Machine 업데이트')

# Samsung Health
hubs['Samsung Health']['spoke_urls']['Samsung Health Data Ecosystem (GUIDE)'] = \
    'https://frontbuffer.net/tech/how-to-backup-samsung-health-data-before-account-deletion/'
hubs['Samsung Health']['spoke_urls']['Samsung Health Data Ecosystem (COMPARISON)'] = \
    'https://frontbuffer.net/tech/samsung-health-vs-google-health-connect-feature-comparison/'
hubs['Samsung Health']['internal_links'] = [
    'https://frontbuffer.net/tech/how-to-backup-samsung-health-data-before-account-deletion/',
    'https://frontbuffer.net/tech/samsung-health-vs-google-health-connect-feature-comparison/',
    'PENDING'
]
print('✅ Samsung Health 업데이트')

pipe['_last_updated'] = datetime.datetime.utcnow().isoformat()
json.dump(pipe, open('content_pipeline.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('완료')
