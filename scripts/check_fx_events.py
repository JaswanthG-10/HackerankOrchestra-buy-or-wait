import pandas as pd

df_events = pd.read_csv('dataset/financial_events.csv')
df_prof = pd.read_csv('dataset/financial_profiles.csv').set_index('user_id')
df_rates = pd.read_csv('dataset/exchange_rates.csv')

# Find events where event currency != user home_currency
foreign = []
for idx, r in df_events.iterrows():
    u = r['user_id']
    home_curr = df_prof.loc[u, 'home_currency']
    if r['currency'] != home_curr:
        foreign.append({
            'event_id': r['event_id'],
            'user_id': u,
            'home_currency': home_curr,
            'event_currency': r['currency'],
            'amount': r['amount'],
            'settlement_date': r['settlement_date'],
            'event_date': r['event_date'],
            'status': r['status']
        })

df_foreign = pd.DataFrame(foreign)
print('Total foreign-currency events:', len(df_foreign))
if len(df_foreign) > 0:
    print(df_foreign.head(15))
