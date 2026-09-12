import pandas as pd
import numpy as np

gt = pd.read_csv('dataset/sample_requests.csv')
profs = pd.read_csv('dataset/financial_profiles.csv')
pred = pd.read_csv('sample_output.csv')

focus_ids = ['request_02', 'request_03', 'request_07', 'request_10', 'request_17', 'request_25']

for rid in focus_ids:
    r = gt[gt['request_id'] == rid].iloc[0]
    p = profs[profs['user_id'] == r['user_id']].iloc[0]
    pr = pred[pred['request_id'] == rid].iloc[0]
    
    bal = p['current_available_balance']
    min_b = p['minimum_balance_to_keep']
    init_hd = bal - min_b
    
    exp_safe = r['amount_safe_to_pay']
    pred_safe = pr['amount_safe_to_pay']
    
    exp_outflow = init_hd - exp_safe
    pred_outflow = init_hd - pred_safe
    
    print(f"=== {rid} ({r['user_id']}) ===")
    print(f"  Date: {r['request_date']} | Req Amount: {r['requested_amount']} | Currency: {p['home_currency']}")
    print(f"  Balance: {bal} | MinKeep: {min_b} | Initial Headroom: {init_hd}")
    print(f"  Expected Safe:  {exp_safe} -> Implied Outflow: {exp_outflow}")
    print(f"  Predicted Safe: {pred_safe} -> Model Outflow:   {pred_outflow}")
    print(f"  Difference in Outflow: {pred_outflow - exp_outflow:+.2f}")
    print(f"  Expected Status: {r['affordability_status']} | Method: {r['recommended_payment_method']}")
    print(f"  Protect: {p['expense_categories_to_protect']}")
