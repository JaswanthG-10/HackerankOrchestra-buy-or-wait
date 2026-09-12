import pandas as pd
df_events = pd.read_csv('dataset/financial_events.csv')
u2_events = df_events[df_events['user_id'] == 'user_02']

# Check all events in July 2025 (or monthly averages)
july = u2_events[(u2_events['event_date'] >= '2025-07-05') & (u2_events['event_date'] < '2025-07-15')]
print('July 5 to July 15 expenses:')
print(july[['event_id', 'description', 'category', 'amount', 'event_date']].to_string())
print('Sum July 5-15:', july['amount'].sum())
print('Sum with pending debit (1651100):', july['amount'].sum() + 1651100)
