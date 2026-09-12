import sys, os
sys.path.insert(0, os.path.abspath('.'))
import pandas as pd
from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)

u08 = events['user_08']
df = pd.DataFrame([e.__dict__ for e in u08])
print('=== User 08 events between day 7 and day 15 ===')
for y, m in [(2024, 11), (2024, 12), (2025, 1)]:
    start_d = f'{y}-{m:02d}-07'
    end_d = f'{y}-{m:02d}-15'
    sub = df[(df['event_date'] >= start_d) & (df['event_date'] < end_d)]
    total = sub['amount'].sum()
    print('Month', y, m, 'sum:', total)
    print(sub[['description', 'category', 'amount', 'event_date']].to_string())
