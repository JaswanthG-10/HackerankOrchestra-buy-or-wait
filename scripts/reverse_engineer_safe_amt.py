import sys, os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
from code.loader import load_profiles

profiles = load_profiles()
df_samples = pd.read_csv('dataset/sample_requests.csv')

print('ReqID | User | ReqAmt | Balance | MinBal | Excess | GT_Safe | Diff')
for _, r in df_samples.iterrows():
    u = r['user_id']
    prof = profiles[u]
    excess = prof.current_available_balance - prof.minimum_balance_to_keep
    safe = float(r['amount_safe_to_pay'])
    diff = excess - safe
    print(r['request_id'], u, 'Req:', r['requested_amount'], 'Excess:', round(excess, 2), 'Safe:', round(safe, 2), 'Diff:', round(diff, 2))
