import os
import sys
import pandas as pd
import numpy as np

from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events, load_requests, load_message_cache
from scripts.test_timeline_simulator import simulate_user_90_days

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events_dict = load_financial_events(profiles, rates, img_cache)
msg_cache = load_message_cache()
sample_reqs = load_requests(use_samples=True)
gt_df = pd.read_csv("dataset/sample_requests.csv").set_index("request_id")

print(f"{'Req ID':<12} {'User':<10} {'Exp Safe':<12} {'Sim Headroom':<14} {'Pred Safe':<12} {'Diff':<12} {'Match'}")
print("-" * 80)

diffs = []
for req in sample_reqs:
    rid = req.request_id
    prof = profiles[req.user_id]
    evs = events_dict.get(req.user_id, [])
    msgs = msg_cache.get(req.user_id, [])
    
    traj, min_hd, min_dt = simulate_user_90_days(
        profile=prof,
        raw_events=evs,
        user_messages=msgs,
        request_date=req.request_date
    )
    
    pred_safe = max(0.0, min(req.requested_amount, min_hd))
    exp_safe = gt_df.loc[rid, "amount_safe_to_pay"]
    diff = pred_safe - exp_safe
    diffs.append(abs(diff))
    
    status = "EXACT" if abs(diff) < 0.05 else ("CLOSE" if abs(diff) < 10.0 else f"{diff:+.2f}")
    print(f"{rid:<12} {req.user_id:<10} {exp_safe:<12.2f} {min_hd:<14.2f} {pred_safe:<12.2f} {diff:<12.2f} {status}")

print("=" * 80)
print(f"Mean Absolute Error (Safe Amount): {np.mean(diffs):.2f}")
print(f"Exact matches (<0.05): {sum(d < 0.05 for d in diffs)} / {len(diffs)}")
print(f"Close matches (<10):   {sum(d < 10.0 for d in diffs)} / {len(diffs)}")
