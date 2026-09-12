import sys, os
sys.path.insert(0, os.path.abspath('.'))
import pandas as pd
from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)

u03 = events['user_03']
df = pd.DataFrame([e.__dict__ for e in u03])
print('=== User 03 events between day 3 and day 15 ===')
for m in [6, 7, 8]:
    start_d = f'2019-{m:02d}-03'
    end_d = f'2019-{m:02d}-15'
    sub = df[(df['event_date'] >= start_d) & (df['event_date'] < end_d)]
    total = sub['amount'].sum()
    print('Month', m, 'sum:', total)
    print(sub[['description', 'category', 'amount', 'event_date']].to_string())
