import pandas as pd
from datetime import datetime, timedelta

df_events = pd.read_csv('dataset/financial_events.csv')
df_rates = pd.read_csv('dataset/exchange_rates.csv')
df_profiles = pd.read_csv('dataset/financial_profiles.csv').set_index('user_id')

# Look at user_01 (request_01: date 2024-03-03, req_amt: 25256, balance: 58481.1, min_bal: 18000)
u1_events = df_events[df_events['user_id'] == 'user_01'].copy()
print(f'User 01 total events: {len(u1_events)}')
print(u1_events['status'].value_counts())
print(u1_events[u1_events['event_date'] >= '2024-03-01'].head(15).to_string())
