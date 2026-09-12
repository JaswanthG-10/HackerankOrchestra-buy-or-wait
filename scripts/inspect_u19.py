import sys, os
sys.path.insert(0, os.path.abspath('.'))
import pandas as pd
from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)

u19 = events['user_19']
df = pd.DataFrame([e.__dict__ for e in u19])
print('=== User 19 profile ===')
print('Balance:', profiles['user_19'].current_available_balance, 'Min:', profiles['user_19'].minimum_balance_to_keep)
print('Excess:', profiles['user_19'].current_available_balance - profiles['user_19'].minimum_balance_to_keep)
print('=== User 19 events in Aug 2024 (Aug 4 to 15) ===')
aug = df[(df['event_date'] >= '2024-08-04') & (df['event_date'] < '2024-08-15')]
print(aug[['event_id', 'description', 'category', 'amount', 'event_date']].to_string())
print('Aug 4-15 sum:', aug['amount'].sum())
