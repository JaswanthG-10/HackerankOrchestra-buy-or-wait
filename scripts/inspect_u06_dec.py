import sys, os
sys.path.insert(0, os.path.abspath('.'))
import pandas as pd
from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)

u06 = events['user_06']
df = pd.DataFrame([e.__dict__ for e in u06])
print('=== User 06 events Dec 3 to Dec 15 2025 ===')
dec = df[(df['event_date'] >= '2025-12-03') & (df['event_date'] < '2025-12-15')]
print(dec[['event_id', 'description', 'category', 'amount', 'event_date']].to_string())
print('Sum:', dec['amount'].sum())
