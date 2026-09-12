import pandas as pd
import numpy as np

gt = pd.read_csv("dataset/sample_requests.csv")
pred = pd.read_csv("sample_output.csv")

merged = pd.merge(gt, pred, on="request_id", suffixes=("_expected", "_predicted"))

print(f"Total evaluated samples: {len(merged)}")

# Safe amount comparison
gt_safe = merged["amount_safe_to_pay_expected"].fillna(0)
pred_safe = merged["amount_safe_to_pay_predicted"].fillna(0)
safe_diff = pred_safe - gt_safe
abs_safe_diff = np.abs(safe_diff)

exact_safe_matches = (abs_safe_diff < 0.05).sum()
close_safe_matches = (abs_safe_diff < 10.0).sum()
mae_safe = abs_safe_diff.mean()

# Status comparison
status_matches = (merged["affordability_status_expected"] == merged["affordability_status_predicted"]).sum()

# Method comparison
method_matches = (merged["recommended_payment_method_expected"] == merged["recommended_payment_method_predicted"]).sum()

# Plan comparison
plan_matches = (merged["payment_plan_expected"].fillna("") == merged["payment_plan_predicted"].fillna("")).sum()

# Earliest date comparison
date_matches = (merged["earliest_date_for_full_payment_expected"].fillna("") == merged["earliest_date_for_full_payment_predicted"].fillna("")).sum()

# Spending changes comparison
def norm_sc(x):
    if pd.isna(x) or str(x).strip() == "" or str(x).strip() == "none":
        return "none"
    parts = sorted([p.strip() for p in str(x).split("|") if p.strip()])
    return "|".join(parts) if parts else "none"

sc_matches = (merged["spending_changes_needed_expected"].apply(norm_sc) == merged["spending_changes_needed_predicted"].apply(norm_sc)).sum()

print("=" * 80)
print("CURRENT BENCHMARK BASELINE METRICS:")
print(f"Amount Safe Exact Match (<0.05): {exact_safe_matches}/{len(merged)} ({exact_safe_matches/len(merged)*100:.1f}%)")
print(f"Amount Safe Close Match (<10):   {close_safe_matches}/{len(merged)} ({close_safe_matches/len(merged)*100:.1f}%)")
print(f"Amount Safe Mean Absolute Error: {mae_safe:.2f}")
print(f"Earliest Date Accuracy:          {date_matches}/{len(merged)} ({date_matches/len(merged)*100:.1f}%)")
print(f"Status Accuracy:                 {status_matches}/{len(merged)} ({status_matches/len(merged)*100:.1f}%)")
print(f"Method Accuracy:                 {method_matches}/{len(merged)} ({method_matches/len(merged)*100:.1f}%)")
print(f"Plan Accuracy:                   {plan_matches}/{len(merged)} ({plan_matches/len(merged)*100:.1f}%)")
print(f"Spending Changes Accuracy:       {sc_matches}/{len(merged)} ({sc_matches/len(merged)*100:.1f}%)")
print("=" * 80)

print("\nMISMATCH TABLE (ALL 25 SAMPLES):")
cols = [
    "request_id",
    "amount_safe_to_pay_expected", "amount_safe_to_pay_predicted",
    "affordability_status_expected", "affordability_status_predicted",
    "recommended_payment_method_expected", "recommended_payment_method_predicted",
    "earliest_date_for_full_payment_expected", "earliest_date_for_full_payment_predicted",
    "spending_changes_needed_expected", "spending_changes_needed_predicted"
]

for idx, row in merged.iterrows():
    diff = row["amount_safe_to_pay_predicted"] - row["amount_safe_to_pay_expected"]
    is_safe_diff = abs(diff) > 0.05
    is_status_diff = row["affordability_status_expected"] != row["affordability_status_predicted"]
    is_method_diff = row["recommended_payment_method_expected"] != row["recommended_payment_method_predicted"]
    is_date_diff = str(row["earliest_date_for_full_payment_expected"]) != str(row["earliest_date_for_full_payment_predicted"])
    is_plan_diff = str(row["payment_plan_expected"]) != str(row["payment_plan_predicted"])
    is_sc_diff = norm_sc(row["spending_changes_needed_expected"]) != norm_sc(row["spending_changes_needed_predicted"])
    
    flags = []
    if is_safe_diff: flags.append(f"SafeDiff:{diff:+.2f}")
    if is_status_diff: flags.append("Status")
    if is_method_diff: flags.append("Method")
    if is_plan_diff: flags.append("Plan")
    if is_date_diff: flags.append("Date")
    if is_sc_diff: flags.append("SpendingChanges")
    
    flag_str = " | ".join(flags) if flags else "PERFECT"
    print(f"[{row['request_id']}] {flag_str}")
    if flags:
        print(f"  Exp Safe: {row['amount_safe_to_pay_expected']}  Pred Safe: {row['amount_safe_to_pay_predicted']} (Diff: {diff:+.2f})")
        print(f"  Exp Status: {row['affordability_status_expected']}  Pred Status: {row['affordability_status_predicted']}")
        print(f"  Exp Method: {row['recommended_payment_method_expected']}  Pred Method: {row['recommended_payment_method_predicted']}")
        print(f"  Exp Earliest: {row['earliest_date_for_full_payment_expected']}  Pred Earliest: {row['earliest_date_for_full_payment_predicted']}")
        print(f"  Exp Plan: {row['payment_plan_expected']}  Pred Plan: {row['payment_plan_predicted']}")
        print(f"  Exp Changes: {row['spending_changes_needed_expected']}  Pred Changes: {row['spending_changes_needed_predicted']}")
        print("-" * 60)
