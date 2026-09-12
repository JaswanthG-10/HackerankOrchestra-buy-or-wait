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

for req in samples:
    u = req.user_id
    prof = profiles[u]
    gt = df_samples_gt.loc[req.request_id]
    gt_safe = float(gt['amount_safe_to_pay'])
    gt_status = str(gt['affordability_status'])
    gt_method = str(gt['recommended_payment_method'])
    gt_earliest = str(gt['earliest_date_for_full_payment'])
    print(req.request_id, u, 'Req:', req.requested_amount, 'GT_Safe:', gt_safe, 'GT_Status:', gt_status, 'GT_Method:', gt_method, 'GT_Earliest:', gt_earliest)
