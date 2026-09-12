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

def simulate_user_90_days(req, stop_events=None, reduce_events=None):
    stop_events = stop_events or set()
    reduce_events = reduce_events or {}
    
    u = req.user_id
    prof = profiles[u]
    u_events = events[u]
    u_msgs = user_messages.get(u, [])
    
    resolved = resolve_user_events(u, u_events, prof, u_msgs, req.request_date)
    ev_list = resolved['events']
    
    req_dt = datetime.strptime(req.request_date, '%Y-%m-%d')
    
    # 1. Historical transactions up to req_date
    history = [e for e in ev_list if e.event_date <= req.request_date and e.status == 'settled']
    
    # Identify distinct recurring transactions by description
    # Find the most recent occurrence of each description
    desc_last_event = {}
    for e in history:
        desc_last_event[e.description] = e
        
    # Salary
    sal_day = 15
    sal_amount = 0.0
    if resolved['salary_date']:
        sal_day = datetime.strptime(resolved['salary_date'], '%Y-%m-%d').day
    
    sal_events = [e for e in history if e.direction == 'credit' and e.category == 'salary']
    if sal_events:
        sal_amount = sal_events[-1].amount
        if not resolved['salary_date']:
            sal_day = datetime.strptime(sal_events[-1].event_date, '%Y-%m-%d').day

    if resolved['salary_update_amt'] is not None:
        sal_amount = resolved['salary_update_amt']
    if resolved['salary_ended']:
        sal_amount = 0.0

    # Recurring debits: take all debit events from the last 30 days before req_date
    last_30_start = req_dt - timedelta(days=31)
    recent_debits = [e for e in history if e.direction == 'debit' and datetime.strptime(e.event_date, '%Y-%m-%d') >= last_30_start]
    
    # Future scheduled / pending events from dataset
    future_events = [e for e in ev_list if e.settlement_date >= req.request_date]
    
    # Project 90 days
    curr_bal = prof.current_available_balance
    balances = []
    
    for day_offset in range(90):
        current_dt = req_dt + timedelta(days=day_offset)
        cur_date_str = current_dt.strftime('%Y-%m-%d')
        
        credits_today = 0.0
        debits_today = 0.0
        
        # Salary credit
        if not resolved['salary_ended'] and current_dt.day == sal_day:
            credits_today += sal_amount
            
        # Confirmed invoices
        for inv in resolved['confirmed_invoices']:
            if inv['date'] == cur_date_str:
                credits_today += inv['amount']
                
        # Scheduled/pending events
        for fe in future_events:
            if fe.settlement_date == cur_date_str:
                if fe.direction == 'credit' and fe.status == 'scheduled':
                    credits_today += fe.amount
                elif fe.direction == 'debit':
                    debits_today += fe.amount
                    
        # Recurring debits from recent monthly template
        if day_offset > 0: # on day 0, curr_bal already reflects settled events up to req_date
            for rd in recent_debits:
                rd_day = datetime.strptime(rd.event_date, '%Y-%m-%d').day
                if current_dt.day == rd_day:
                    amt = rd.amount
                    if rd.event_id in stop_events:
                        amt = 0.0
                    elif rd.event_id in reduce_events:
                        amt = reduce_events[rd.event_id]
                    debits_today += amt
                    
        curr_bal += (credits_today - debits_today)
        balances.append((cur_date_str, curr_bal))
        
    return balances

print('Testing monthly template replay on sample requests...')
for req in samples:
    gt = df_samples_gt.loc[req.request_id]
    gt_safe = float(gt['amount_safe_to_pay'])
    gt_earliest = str(gt['earliest_date_for_full_payment'])
    
    balances = simulate_user_90_days(req)
    prof = profiles[req.user_id]
    
    # Safety before salary
    min_headroom = min(bal - prof.minimum_balance_to_keep for dt, bal in balances)
    calc_safe = max(0.0, min(req.requested_amount, min_headroom))
    
    diff = abs(calc_safe - gt_safe)
    print(req.request_id, 'GT_Safe:', round(gt_safe, 2), 'Calc_Safe:', round(calc_safe, 2), 'Diff:', round(diff, 2))
