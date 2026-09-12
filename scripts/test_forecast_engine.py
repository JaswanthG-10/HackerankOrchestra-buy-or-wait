import sys, os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

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
from code.models import UserProfile, FinancialEvent, RequestItem

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)
options = load_payment_options()
samples = load_requests(use_samples=True)
df_samples_gt = pd.read_csv('dataset/sample_requests.csv').set_index('request_id')
msg_facts = get_message_facts()

user_messages = {}
for m in msg_facts.values():
    u = m['user_id']
    if u not in user_messages:
        user_messages[u] = []
    user_messages[u].append(m)

def analyze_user_cashflow(req: RequestItem):
    u = req.user_id
    prof = profiles[u]
    u_events = events[u]
    u_msgs = user_messages.get(u, [])
    
    resolved = resolve_user_events(u, u_events, prof, u_msgs, req.request_date)
    ev_list = resolved['events']
    
    req_dt = datetime.strptime(req.request_date, '%Y-%m-%d')
    gt = df_samples_gt.loc[req.request_id]
    gt_safe = float(gt['amount_safe_to_pay'])
    
    # Check pending debits
    pending_debits = [e for e in ev_list if e.status == 'pending' and e.direction == 'debit' and e.settlement_date >= req.request_date]
    pending_sum = sum(e.amount for e in pending_debits)
    
    # Excess balance
    excess = prof.current_available_balance - prof.minimum_balance_to_keep
    
    # Check debits between req_date and next salary
    # Salary date
    sal_day = 15
    if resolved['salary_date']:
        sal_day = datetime.strptime(resolved['salary_date'], '%Y-%m-%d').day
    
    # Next salary dt
    if req_dt.day < sal_day:
        next_sal_dt = req_dt.replace(day=sal_day)
    else:
        # next month
        m = req_dt.month + 1
        y = req_dt.year
        if m > 12:
            m = 1
            y += 1
        next_sal_dt = datetime(y, m, sal_day)
        
    days_to_sal = (next_sal_dt - req_dt).days
    
    # Compare with GT safe
    diff = excess - gt_safe
    print(f'{req.request_id} ({u}): excess={excess:,.2f}, gt_safe={gt_safe:,.2f}, diff={diff:,.2f}, pending_debits={pending_sum}, days_to_sal={days_to_sal}')

for s in samples[:10]:
    analyze_user_cashflow(s)
