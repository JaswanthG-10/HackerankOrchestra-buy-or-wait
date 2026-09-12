import sys, os
sys.path.insert(0, os.path.abspath('.'))
import pandas as pd
from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)

u15 = events['user_15']
df = pd.DataFrame([e.__dict__ for e in u15])
print('=== User 15 events in Dec 2025 ===')
print(df[(df['event_date'] >= '2025-12-06') & (df['event_date'] <= '2025-12-15')][['event_id', 'description', 'category', 'amount', 'event_date']].to_string())
print('Sum of Dec 6-15 expenses:', df[(df['event_date'] >= '2025-12-06') & (df['event_date'] <= '2025-12-15')]['amount'].sum())
