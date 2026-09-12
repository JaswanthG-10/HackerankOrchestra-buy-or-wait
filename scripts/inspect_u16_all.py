import sys, os
sys.path.insert(0, os.path.abspath('.'))
import pandas as pd
from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)

u16 = events['user_16']
df = pd.DataFrame([e.__dict__ for e in u16])
print('=== User 16 salary and rent ===')
print(df[df['category'].isin(['salary', 'rent'])][['event_id', 'description', 'category', 'amount', 'event_date', 'settlement_date', 'status']].to_string())
