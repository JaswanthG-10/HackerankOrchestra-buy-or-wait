import argparse
import os
import sys
from pathlib import Path
import pandas as pd

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from code.config import (
    OUTPUT_PATH,
    USAGE_REPORT_PATH,
    REQUESTS_PATH,
    SAMPLE_REQUESTS_PATH,
    format_amount
)
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
from code.finance.safety import (
    compute_amount_safe_to_pay,
    compute_earliest_date_for_full_payment
)
from code.planning.installments import evaluate_installment_options
from code.planning.partial import evaluate_partial_payment
from code.planning.spending_changes import evaluate_spending_changes
from code.planning.ranker import rank_plan_candidates
from code.output.explanation import generate_decision_explanation
from code.output.validator import validate_dataframe
from code.evaluation.usage_report import generate_usage_report
from code.models import PlanCandidate, PredictionResult

def solve_request(
    request,
    profiles,
    all_events,
    all_options,
    user_messages
) -> PredictionResult:
    u_id = request.user_id
    prof = profiles[u_id]
    u_events = all_events.get(u_id, [])
    u_msgs = user_messages.get(u_id, [])
    req_opts = all_options.get(request.request_id, [])

    # 1. Resolve events with message evidence
    resolved = resolve_user_events(u_id, u_events, prof, u_msgs, request.request_date)
    events_clean = resolved['events']

    # 2. Compute safety metrics
    safe_amt = compute_amount_safe_to_pay(
        profile=prof,
        events=events_clean,
        resolved_info=resolved,
        request_date=request.request_date,
        requested_amount=request.requested_amount
    )

    earliest_full = compute_earliest_date_for_full_payment(
        profile=prof,
        events=events_clean,
        resolved_info=resolved,
        request_date=request.request_date,
        requested_amount=request.requested_amount,
        amount_safe_to_pay=safe_amt
    )

    # 3. Generate candidate plans
    candidates = []

    # Option A: Full payment today
    if 'full_payment' in prof.payment_methods_user_will_consider and safe_amt >= request.requested_amount:
        p_str = format_amount(request.requested_amount)
        candidates.append(PlanCandidate(
            method='full_payment',
            affordability_status='affordable_now',
            payment_plan=f'{request.request_date}:{p_str}',
            schedule=[(request.request_date, request.requested_amount)],
            completes_by_deadline=True,
            spending_changes=[],
            total_amount_paid=request.requested_amount,
            start_date=request.request_date,
            num_payments=1,
            payment_option_id=None,
            is_safe=True
        ))

    # Option B: Partial payment
    partial_cand = evaluate_partial_payment(
        profile=prof,
        events=events_clean,
        resolved_info=resolved,
        request=request,
        amount_safe_to_pay=safe_amt,
        earliest_date_for_full_payment=earliest_full
    )
    if partial_cand:
        candidates.append(partial_cand)

    # Option C: Installment options
    inst_cands = evaluate_installment_options(
        profile=prof,
        events=events_clean,
        resolved_info=resolved,
        request=request,
        options=req_opts
    )
    candidates.extend(inst_cands)

    # Option D: Spending changes to enable full payment today
    sc_cand = evaluate_spending_changes(
        profile=prof,
        events=events_clean,
        resolved_info=resolved,
        request=request,
        amount_safe_to_pay=safe_amt
    )
    if sc_cand:
        candidates.append(sc_cand)

    # Option E: Wait for full payment later
    if 'full_payment' in prof.payment_methods_user_will_consider and earliest_full and earliest_full > request.request_date:
        if earliest_full <= request.desired_completion_date:
            p_str = format_amount(request.requested_amount)
            candidates.append(PlanCandidate(
                method='wait',
                affordability_status='affordable_later',
                payment_plan=f'{earliest_full}:{p_str}',
                schedule=[(earliest_full, request.requested_amount)],
                completes_by_deadline=True,
                spending_changes=[],
                total_amount_paid=request.requested_amount,
                start_date=earliest_full,
                num_payments=1,
                payment_option_id=None,
                is_safe=True
            ))

    # 4. Rank candidates
    winning_candidate = rank_plan_candidates(candidates)

    # 5. Format decision fields
    if winning_candidate:
        status = winning_candidate.affordability_status
        method = winning_candidate.method
        plan = winning_candidate.payment_plan
        earliest_date_str = earliest_full or ''
        if status == 'affordable_now':
            earliest_date_str = request.request_date
        changes_str = '|'.join(winning_candidate.spending_changes) if winning_candidate.spending_changes else 'none'
    else:
        status = 'not_affordable'
        method = 'not_recommended'
        plan = 'none'
        earliest_date_str = ''
        changes_str = 'none'

    explanation = generate_decision_explanation(
        profile=prof,
        request=request,
        candidate=winning_candidate,
        amount_safe_to_pay=safe_amt,
        earliest_date_for_full_payment=earliest_date_str,
        all_events=u_events
    )

    return PredictionResult(
        request_id=request.request_id,
        amount_safe_to_pay=safe_amt,
        affordability_status=status,
        recommended_payment_method=method,
        payment_plan=plan,
        earliest_date_for_full_payment=earliest_date_str,
        spending_changes_needed=changes_str,
        decision_explanation=explanation
    )

def main():
    parser = argparse.ArgumentParser(description='Buy or Wait? Solver')
    parser.add_argument('--mode', choices=['sample', 'full'], default='full', help='Run mode (sample or full)')
    args = parser.parse_args()

    use_samples = (args.mode == 'sample')
    print(f'Starting Buy or Wait? Solver in {args.mode.upper()} mode...')

    profiles = load_profiles()
    rates = load_exchange_rates()
    img_cache = load_image_cache()
    all_events = load_financial_events(profiles, rates, img_cache)
    all_options = load_payment_options()
    requests_list = load_requests(use_samples=use_samples)
    msg_facts = get_message_facts()

    user_messages = {}
    for m in msg_facts.values():
        u = m.get('user_id')
        if u:
            if u not in user_messages:
                user_messages[u] = []
            user_messages[u].append(m)

    results = []
    for req in requests_list:
        res = solve_request(
            request=req,
            profiles=profiles,
            all_events=all_events,
            all_options=all_options,
            user_messages=user_messages
        )
        results.append(res.to_csv_row())

    df_out = pd.DataFrame(results)

    # Load source requests dataframe for validation
    src_path = SAMPLE_REQUESTS_PATH if use_samples else REQUESTS_PATH
    df_src = pd.read_csv(src_path)

    # Validate output
    valid, errors = validate_dataframe(df_out, df_src)
    if not valid:
        print('Validation FAILED with errors:')
        for err in errors[:10]:
            print('  -', err)
        sys.exit(1)
    else:
        print('Validation PASSED successfully!')

    # Compare with ground truth if in sample mode
    if use_samples:
        df_out.to_csv('sample_output.csv', index=False)
        df_gt = pd.read_csv(SAMPLE_REQUESTS_PATH)
        matches_status = (df_out['affordability_status'] == df_gt['affordability_status']).sum()
        matches_method = (df_out['recommended_payment_method'] == df_gt['recommended_payment_method']).sum()
        matches_plan = (df_out['payment_plan'] == df_gt['payment_plan']).sum()
        print(f'Sample Benchmark Results ({len(df_out)} total):')
        print(f'  Status Accuracy: {matches_status}/{len(df_out)} ({matches_status/len(df_out)*100:.1f}%)')
        print(f'  Method Accuracy: {matches_method}/{len(df_out)} ({matches_method/len(df_out)*100:.1f}%)')
        print(f'  Plan Accuracy:   {matches_plan}/{len(df_out)} ({matches_plan/len(df_out)*100:.1f}%)')
    else:
        # Write root-level output.csv
        df_out.to_csv(OUTPUT_PATH, index=False)
        print(f'Successfully generated {OUTPUT_PATH} ({len(df_out)} rows)')

        # Generate usage report
        generate_usage_report(
            output_md_path=USAGE_REPORT_PATH,
            total_requests=len(df_out)
        )

if __name__ == '__main__':
    main()
