import pandas as pd
df_events = pd.read_csv('dataset/financial_events.csv')
u1_events = df_events[df_events['user_id'] == 'user_01'].sort_values('event_date')
print(u1_events.groupby('description')[['event_date', 'amount', 'category', 'flexibility']].agg(list).to_string())
