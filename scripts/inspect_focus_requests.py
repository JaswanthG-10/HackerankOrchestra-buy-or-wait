import pandas as pd
from code.loader import load_profiles, load_financial_events, load_payment_options, load_requests, load_message_cache, load_exchange_rates, load_image_cache
from code.finance.event_resolver import resolve_user_events
from code.finance.forecast import build_forecast_timeline

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
all_events = load_financial_events(profiles, rates, img_cache)
requests_list = load_requests(use_samples=True)
user_messages = load_message_cache()
gt_df = pd.read_csv('dataset/sample_requests.csv').set_index('request_id')

for req_id in ['request_02', 'request_03', 'request_10', 'request_11', 'request_19', 'request_21', 'request_22']:
    req = [r for r in requests_list if r.request_id == req_id][0]
    gt = gt_df.loc[req_id]
    prof = profiles[req.user_id]
    evs = all_events[req.user_id]
    resolved = resolve_user_events(req.user_id, evs, prof, user_messages.get(req.user_id, []), req.request_date)
    print(f'=== {req_id} ({req.user_id}) Date: {req.request_date} Requested: {req.requested_amount} ===')
    print('   GT Safe:', gt['amount_safe_to_pay'], 'Status:', gt['affordability_status'], 'Method:', gt['recommended_payment_method'], 'Date:', gt['earliest_date_for_full_payment'])
    print('   Profile: Bal:', prof.current_available_balance, 'MinKeep:', prof.minimum_balance_to_keep, 'Day0 Headroom:', prof.current_available_balance - prof.minimum_balance_to_keep)
