import pandas as pd

df_samples = pd.read_csv('dataset/sample_requests.csv')
df_profiles = pd.read_csv('dataset/financial_profiles.csv').set_index('user_id')
df_options = pd.read_csv('dataset/request_payment_options.csv')

with open('samples_summary.txt', 'w', encoding='utf-8') as out:
    for _, r in df_samples.iterrows():
        req_id = r['request_id']
        u_id = r['user_id']
        prof = df_profiles.loc[u_id]
        opts = df_options[df_options['request_id'] == req_id]
        
        out.write(f"=== {req_id} ({u_id}) ===\n")
        out.write(f"Date: {r['request_date']}, Type: {r['request_type']}, Amount: {r['requested_amount']} {prof['home_currency']}\n")
        out.write(f"Desired Completion: {r['desired_completion_date']}, Allows Partial: {r['allows_partial_payment']}\n")
        out.write(f"User Balance: {prof['current_available_balance']}, Min Balance: {prof['minimum_balance_to_keep']}, Methods: {prof['payment_methods_user_will_consider']}, Max Inst Months: {prof['max_installment_months']}\n")
        out.write(f"Protect: {prof['expense_categories_to_protect']}, Reduce: {prof['expense_categories_user_is_willing_to_reduce']}, Stop: {prof['expense_categories_user_is_willing_to_stop']}\n")
        out.write(f"GROUND TRUTH:\n")
        out.write(f"  amount_safe_to_pay: {r['amount_safe_to_pay']}\n")
        out.write(f"  affordability_status: {r['affordability_status']}\n")
        out.write(f"  recommended_payment_method: {r['recommended_payment_method']}\n")
        out.write(f"  payment_plan: {r['payment_plan']}\n")
        out.write(f"  earliest_date_for_full_payment: {r['earliest_date_for_full_payment']}\n")
        out.write(f"  spending_changes_needed: {r['spending_changes_needed']}\n")
        out.write(f"  decision_explanation: {r['decision_explanation']}\n")
        out.write("  Payment Options:\n")
        for _, opt in opts.iterrows():
            out.write(f"    {opt['payment_option_id']}: method={opt['payment_method']}, amt={opt['payment_amount']}, n={opt['number_of_payments']}, 1st_date={opt['first_payment_date']}, freq={opt['payment_frequency_days']}, fee={opt['financing_fee']}, total={opt['total_payable_amount']}\n")
        out.write("\n")

print("Wrote samples_summary.txt successfully")
