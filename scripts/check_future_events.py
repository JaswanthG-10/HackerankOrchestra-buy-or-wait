import pandas as pd

df = pd.read_csv('dataset/financial_events.csv')
df_samples = pd.read_csv('dataset/sample_requests.csv')

print('Check future events for sample users after their request_date:')
for _, r in df_samples.head(15).iterrows():
    u = r['user_id']
    req_date = r['request_date']
    u_events = df[df['user_id'] == u]
    future_ev = u_events[u_events['event_date'] > req_date]
    future_settle = u_events[u_events['settlement_date'] > req_date]
    print(r['request_id'], u, 'req_date:', req_date, 'events:', len(u_events), 'future_event_date:', len(future_ev), 'future_settlement_date:', len(future_settle))
