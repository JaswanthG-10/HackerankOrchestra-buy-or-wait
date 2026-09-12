import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events, load_requests, load_message_cache
from scripts.test_timeline_simulator import simulate_user_90_days

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events_dict = load_financial_events(profiles, rates, img_cache)
msg_cache = load_message_cache()
sample_reqs = load_requests(use_samples=True)
gt_df = pd.read_csv("dataset/sample_requests.csv").set_index("request_id")

def find_earliest_safe_full_payment_date(
    profile,
    events,
    user_messages,
    request_date: str,
    requested_amount: float,
    max_days: int = 90
) -> Optional[str]:
    req_dt = datetime.strptime(request_date, "%Y-%m-%d")
    
    # Test candidate dates starting from request_date
    for d in range(max_days + 1):
        cand_dt = req_dt + timedelta(days=d)
        cand_str = cand_dt.strftime("%Y-%m-%d")
        
        # Test full payment on cand_str
        traj, min_hd, _ = simulate_user_90_days(
            profile=profile,
            raw_events=events,
            user_messages=user_messages,
            request_date=request_date,
            payment_schedule=[(cand_str, requested_amount)]
        )
        
        if min_hd >= 0.0:
            return cand_str
            
    return None

test_rids = ["request_03", "request_08", "request_13", "request_18", "request_22", "request_23"]
for rid in test_rids:
    req = [r for r in sample_reqs if r.request_id == rid][0]
    prof = profiles[req.user_id]
    evs = events_dict.get(req.user_id, [])
    msgs = msg_cache.get(req.user_id, [])
    
    earliest_date = find_earliest_safe_full_payment_date(
        profile=prof,
        events=evs,
        user_messages=msgs,
        request_date=req.request_date,
        requested_amount=req.requested_amount
    )
    exp_date = str(gt_df.loc[rid, "earliest_date_for_full_payment"])
    print(f"[{rid}] Expected: {exp_date} | Computed: {earliest_date} | Match: {str(exp_date) == str(earliest_date)}")
