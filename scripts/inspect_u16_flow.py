import sys, os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
from datetime import datetime, timedelta

from code.loader import (
    load_profiles,
    load_exchange_rates,
    load_image_cache,
    load_financial_events,
    load_payment_options,
    load_requests
)
from code.evidence.message_parser import get_message_facts
from code.finance.event_resolver import resolve_user_events

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)
samples = load_requests(use_samples=True)
df_samples_gt = pd.read_csv('dataset/sample_requests.csv').set_index('request_id')
msg_facts = get_message_facts()

user_messages = {}
for m in msg_facts.values():
    u = m['user_id']
    if u not in user_messages:
        user_messages[u] = []
    user_messages[u].append(m)

# Let's inspect user_16 with proper monthly inflow/outflow
req = [s for s in samples if s.request_id == 'request_16'][0]
u = req.user_id
prof = profiles[u]
u_events = events[u]
u_msgs = user_messages.get(u, [])
resolved = resolve_user_events(u, u_events, prof, u_msgs, req.request_date)

print('User 16 resolved events count:', len(resolved['events']))
req_dt = datetime.strptime(req.request_date, '%Y-%m-%d')
print('Req date:', req.request_date, 'Balance:', prof.current_available_balance, 'Min:', prof.minimum_balance_to_keep)

# Check all events between 2023-08-12 and 2023-09-12
fut = [e for e in resolved['events'] if e.settlement_date >= req.request_date]
for f in fut:
    print('Future event:', f.event_id, f.description, f.direction, f.amount, f.settlement_date, f.status)
