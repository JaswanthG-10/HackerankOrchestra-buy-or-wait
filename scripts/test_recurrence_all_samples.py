import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter

events = pd.read_csv('dataset/financial_events.csv')
sample_reqs = pd.read_csv('dataset/sample_requests.csv')

for idx, req in sample_reqs.iterrows():
    u_id = req['user_id']
    req_dt = req['request_date']
    
    u_events = events[(events['user_id'] == u_id) & (events['event_date'] <= req_dt) & (events['status'] == 'settled') & (events['direction'] == 'debit')].copy()
    u_events['event_date'] = pd.to_datetime(u_events['event_date'])
    u_events = u_events.sort_values('event_date')
    
    # Check groups
    print(f"\n==================== {req['request_id']} ({u_id}) Request Date: {req_dt} ====================")
    desc_groups = {}
    for _, ev in u_events.iterrows():
        desc = ev['description']
        desc_groups.setdefault(desc, []).append(ev)
        
    for desc, evs in desc_groups.items():
        if len(evs) >= 2:
            dates = [e['event_date'] for e in evs]
            deltas = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            med_delta = np.median(deltas) if deltas else 0
            amounts = [e['amount'] for e in evs]
            cat = evs[-1]['category']
            flex = evs[-1]['flexibility']
            
            freq = "unknown"
            if 6 <= med_delta <= 8:
                freq = f"weekly (weekday {dates[-1].weekday()})"
            elif 13 <= med_delta <= 16:
                freq = f"bi-weekly"
            elif 27 <= med_delta <= 32:
                days = [d.day for d in dates]
                dom = Counter(days).most_common(1)[0][0]
                freq = f"monthly (day {dom})"
            
            if freq != "unknown":
                print(f"  [RECURRING] '{desc}' ({cat}) -> {freq} | Mean: {np.mean(amounts):.2f} | Last: {amounts[-1]:.2f} | Flex: {flex}")
