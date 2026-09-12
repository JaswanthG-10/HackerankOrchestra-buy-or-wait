import pandas as pd
df_events = pd.read_csv('dataset/financial_events.csv')
u2_events = df_events[df_events['user_id'] == 'user_02'].sort_values('event_date')
print('=== USER 02 EVENTS AFTER 2025-07-01 ===')
print(u2_events[u2_events['event_date'] >= '2025-07-01'][['event_id', 'event_type', 'description', 'category', 'direction', 'amount', 'event_date', 'settlement_date', 'status', 'flexibility']].to_string())
