import pandas as pd

df_msg = pd.read_csv('dataset/messages.csv')
for st in ['employer', 'service_provider', 'financial_service', 'bank', 'merchant']:
    print('=== SOURCE TYPE:', st, '===')
    sub = df_msg[df_msg['source_type'] == st]
    for idx, r in sub.head(3).iterrows():
        print(r['message_id'], 'u:', r['user_id'], 'req:', r['request_id'], 'ev:', r['related_event_id'])
        print('  Text:', r['message_text'])
    print()
