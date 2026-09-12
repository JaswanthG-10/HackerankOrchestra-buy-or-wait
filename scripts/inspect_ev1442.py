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
print('=== Event 1442 ===')
print(df[df['event_id'] == 'event_1442'].to_dict(orient='records'))
