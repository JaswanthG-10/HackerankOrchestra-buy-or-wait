import json
with open('code/cache/images.json') as f:
    c = json.load(f)
print('Total cached images:', len(c))
for k in sorted(c.keys()):
    v = c[k]
    print(k, 'event:', v.get('related_event_id'), 'user:', v.get('user_id'), 'req:', v.get('request_id'), 'amt:', v.get('amount'), 'curr:', v.get('currency'), 'doc:', v.get('document_type'))
