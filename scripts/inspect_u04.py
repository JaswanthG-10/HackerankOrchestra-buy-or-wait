import sys, os
sys.path.insert(0, os.path.abspath('.'))
import pandas as pd
from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)

u4_events = events['user_04']
df_u4 = pd.DataFrame([e.__dict__ for e in u4_events])
print('User 04 events by description and day of month:')
for desc, grp in df_u4.groupby('description'):
    if len(grp) >= 2:
        days = [int(d.split('-')[2]) for d in grp['event_date']]
        amts = grp['amount'].tolist()
        print(desc, 'cat:', grp['category'].iloc[0], 'n:', len(grp), 'days:', days[:4], 'amts:', amts[:4])
