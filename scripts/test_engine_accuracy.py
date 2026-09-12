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

def build_forecast(user_id: str, request_date: str, stop_events: set = None, reduce_events: dict = None):
    stop_events = stop_events or set()
    reduce_events = reduce_events or {}
    
    prof = profiles[user_id]
    u_events = events[user_id]
    u_msgs = user_messages.get(user_id, [])
    
    resolved = resolve_user_events(user_id, u_events, prof, u_msgs, request_date)
    ev_list = resolved['events']
    
    req_dt = datetime.strptime(request_date, '%Y-%m-%d')
    history = [e for e in ev_list if e.event_date < request_date and e.status == 'settled']
    
    # 1. Detect recurring fixed debits
    recurring_debits = {}
    for e in history:
        if e.direction == 'debit':
            d_obj = datetime.strptime(e.event_date, '%Y-%m-%d')
            if e.category in ['rent', 'utilities', 'insurance', 'education', 'debt_repayment', 'subscription', 'healthcare', 'cloud_storage', 'streaming', 'music_subscription', 'gym', 'delivery_membership', 'housing']:
                if e.description not in recurring_debits:
                    recurring_debits[e.description] = {
                        'day': d_obj.day,
                        'amount': e.amount,
                        'category': e.category,
                        'flexibility': e.flexibility,
                        'event_id': e.event_id,
                        'min_allowed': e.minimum_allowed_amount
                    }
                else:
                    recurring_debits[e.description]['day'] = d_obj.day
                    recurring_debits[e.description]['amount'] = e.amount
                    recurring_debits[e.description]['event_id'] = e.event_id

    # 2. Variable categories daily rate
    var_categories = ['groceries', 'transport', 'dining', 'shopping', 'entertainment']
    var_spending = {c: 0.0 for c in var_categories}
    if history:
        earliest_dt = min(datetime.strptime(e.event_date, '%Y-%m-%d') for e in history)
        span_days = max(1, (req_dt - earliest_dt).days)
        for e in history:
            if e.direction == 'debit' and e.category in var_categories:
                var_spending[e.category] += e.amount
        daily_var_burn = sum(var_spending.values()) / span_days
    else:
        daily_var_burn = 0.0

    # 3. Detect salary
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

    # 4. Pending / Scheduled future events
    future_events = [e for e in ev_list if e.settlement_date >= request_date]
    
    # 5. Build 90-day cash trajectory
    balances = []
    curr_bal = prof.current_available_balance
    
    for day_offset in range(90):
        current_dt = req_dt + timedelta(days=day_offset)
        cur_date_str = current_dt.strftime('%Y-%m-%d')
        
        credits_today = 0.0
        debits_today = 0.0
        
        if not resolved['salary_ended'] and current_dt.day == sal_day:
            credits_today += sal_amount
            
        for inv in resolved['confirmed_invoices']:
            if inv['date'] == cur_date_str:
                credits_today += inv['amount']
                
        for fe in future_events:
            if fe.settlement_date == cur_date_str:
                if fe.direction == 'credit' and fe.status == 'scheduled':
                    credits_today += fe.amount
                elif fe.direction == 'debit':
                    debits_today += fe.amount
                    
        for desc, item in recurring_debits.items():
            if current_dt.day == item['day']:
                amt = item['amount']
                if item['event_id'] in stop_events:
                    amt = 0.0
                elif item['event_id'] in reduce_events:
                    amt = reduce_events[item['event_id']]
                debits_today += amt
                
        debits_today += daily_var_burn
        
        curr_bal += (credits_today - debits_today)
        balances.append((cur_date_str, curr_bal))
        
    return balances, recurring_debits, sal_amount, sal_day

print('Testing simulation on all 25 sample requests...')
for req in samples:
    gt = df_samples_gt.loc[req.request_id]
    gt_safe = float(gt['amount_safe_to_pay'])
    gt_status = str(gt['affordability_status'])
    gt_method = str(gt['recommended_payment_method'])
    gt_earliest = str(gt['earliest_date_for_full_payment'])
    
    balances, rec_debits, sal_amt, sal_day = build_forecast(req.user_id, req.request_date)
    prof = profiles[req.user_id]
    
    min_headroom = min(bal - prof.minimum_balance_to_keep for dt, bal in balances)
    calc_safe = max(0.0, min(req.requested_amount, min_headroom))
    
    earliest_full = None
    for dt, bal in balances:
        dt_idx = [b[0] for b in balances].index(dt)
        if all(b[1] - req.requested_amount >= prof.minimum_balance_to_keep for b in balances[dt_idx:]):
            earliest_full = dt
            break
            
    earliest_str = earliest_full if earliest_full else 'nan'
    diff_safe = abs(calc_safe - gt_safe)
    print(req.request_id, 'GT_Safe:', round(gt_safe, 2), 'Calc_Safe:', round(calc_safe, 2), 'Diff:', round(diff_safe, 2), '| GT_Earliest:', gt_earliest, 'Calc:', earliest_str)
