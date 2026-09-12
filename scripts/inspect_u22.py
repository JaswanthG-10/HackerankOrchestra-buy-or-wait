import sys, os
sys.path.insert(0, os.path.abspath('.'))
import pandas as pd
from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)

u22 = events['user_22']
df = pd.DataFrame([e.__dict__ for e in u22])
print('=== User 22 events in Nov/Dec 2024 ===')
print(df[df['event_date'] >= '2024-11-01'][['event_id', 'description', 'category', 'amount', 'event_date', 'settlement_date', 'status', 'flexibility']].to_string())
