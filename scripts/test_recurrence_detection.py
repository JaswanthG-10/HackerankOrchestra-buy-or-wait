import pandas as pd
import numpy as np
from datetime import datetime, timedelta

events = pd.read_csv('dataset/financial_events.csv')
u10 = events[events['user_id'] == 'user_10'].copy()
u10['event_date'] = pd.to_datetime(u10['event_date'])
debits = u10[(u10['direction'] == 'debit') & (u10['status'] == 'settled')].sort_values('event_date')

# Let's inspect intervals for each category or description
for cat, grp in debits.groupby('category'):
    dates = grp['event_date'].tolist()
    if len(dates) >= 3:
        deltas = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        median_delta = np.median(deltas)
        mean_amt = grp['amount'].mean()
        print(f"Category '{cat}': count={len(dates)}, median_delta={median_delta:.1f} days, mean_amt={mean_amt:.2f}")

print("\nSpecific recurring descriptions:")
for desc, grp in debits.groupby('description'):
    dates = grp['event_date'].tolist()
    if len(dates) >= 3:
        deltas = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        median_delta = np.median(deltas)
        print(f"  '{desc}' ({grp['category'].iloc[0]}): count={len(dates)}, median_delta={median_delta:.1f} days, last_amt={grp['amount'].iloc[-1]}")
