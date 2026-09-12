import sys, os
sys.path.insert(0, os.path.abspath('.'))
import pandas as pd
from datetime import datetime

df = pd.read_csv('dataset/financial_events.csv')
for u in ['user_01', 'user_02', 'user_06', 'user_15', 'user_22']:
    u_events = df[df['user_id'] == u]
    print('===', u, '===')
    for desc, grp in u_events.groupby('description'):
        if len(grp) >= 3:
            dates = [datetime.strptime(d, '%Y-%m-%d') for d in grp['event_date']]
            dates.sort()
            diffs = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            days_of_month = [d.day for d in dates]
            amts = grp['amount'].tolist()[:3]
            print(desc, 'n:', len(grp), 'diffs:', diffs[:4], 'days:', days_of_month[:4], 'amts:', amts)
