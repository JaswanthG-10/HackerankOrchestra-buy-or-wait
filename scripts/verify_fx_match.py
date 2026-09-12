import pandas as pd

df_events = pd.read_csv('dataset/financial_events.csv')
df_prof = pd.read_csv('dataset/financial_profiles.csv').set_index('user_id')
df_rates = pd.read_csv('dataset/exchange_rates.csv').set_index(['rate_date', 'from_currency', 'to_currency'])

unmatched = []
for idx, r in df_events.iterrows():
    u = r['user_id']
    home_curr = df_prof.loc[u, 'home_currency']
    ev_curr = r['currency']
    if ev_curr != home_curr:
        key = (r['settlement_date'], ev_curr, home_curr)
        if key not in df_rates.index:
            unmatched.append((r['event_id'], key))

print('Total unmatched foreign events:', len(unmatched))
if unmatched:
    print('Unmatched examples:', unmatched[:5])
