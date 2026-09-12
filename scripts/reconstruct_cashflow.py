import sys, os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events, load_payment_options, load_requests
from code.evidence.message_parser import get_message_facts

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)
options = load_payment_options()
samples = load_requests(use_samples=True)
df_samples_gt = pd.read_csv('dataset/sample_requests.csv').set_index('request_id')
msg_facts = get_message_facts()

for req_id in ['request_01', 'request_02', 'request_03', 'request_04', 'request_06', 'request_19']:
    gt = df_samples_gt.loc[req_id]
    u = gt['user_id']
    prof = profiles[u]
    req_date = gt['request_date']
    u_events = events[u]
    
    excess = prof.current_available_balance - prof.minimum_balance_to_keep
    print('========================================')
    print(req_id, u, 'req_date:', req_date, 'req_amt:', gt['requested_amount'])
    print('Current Bal:', prof.current_available_balance, 'Min Bal:', prof.minimum_balance_to_keep, 'Excess:', excess)
    print('GT Safe:', gt['amount_safe_to_pay'], 'Earliest:', gt['earliest_date_for_full_payment'])
    
    for e in u_events:
        if e.settlement_date >= req_date:
            print('  Event:', e.event_id, e.description, e.direction, e.amount, 'status:', e.status, 'settle:', e.settlement_date)
