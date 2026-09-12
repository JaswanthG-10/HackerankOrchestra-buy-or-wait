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
print('=== User 06 events in Jan 2026 ===')
print(df[df['event_date'] >= '2026-01-01'][['event_id', 'description', 'category', 'amount', 'event_date', 'settlement_date', 'status']].to_string())
