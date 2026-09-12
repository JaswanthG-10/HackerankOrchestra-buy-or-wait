import pandas as pd
df_events = pd.read_csv('dataset/financial_events.csv')
u1_events = df_events[df_events['user_id'] == 'user_01'].sort_values('event_date')
print('Min date:', u1_events['event_date'].min(), 'Max date:', u1_events['event_date'].max())
print(u1_events.tail(20).to_string())
