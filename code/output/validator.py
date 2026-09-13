import re
from pathlib import Path
from typing import List, Tuple
import pandas as pd

from code.config import AFFORDABILITY_STATUSES, PAYMENT_METHODS

REQUIRED_COLUMNS = [
    'request_id',
    'amount_safe_to_pay',
    'affordability_status',
    'recommended_payment_method',
    'payment_plan',
    'earliest_date_for_full_payment',
    'spending_changes_needed',
    'decision_explanation'
]

def validate_dataframe(df: pd.DataFrame, requests_df: pd.DataFrame) -> Tuple[bool, List[str]]:
    errors = []

    # 1. Exact columns & order
    if list(df.columns) != REQUIRED_COLUMNS:
        errors.append(f'Columns mismatch! Expected: {REQUIRED_COLUMNS}, Got: {list(df.columns)}')
        return False, errors

    # 2. Row count & ID coverage
    if len(df) != len(requests_df):
        errors.append(f'Row count mismatch! Expected {len(requests_df)}, Got {len(df)}')

    expected_ids = set(requests_df['request_id'])
    actual_ids = set(df['request_id'])
    if actual_ids != expected_ids:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        if missing:
            errors.append(f'Missing request IDs ({len(missing)}): {list(missing)[:5]}')
        if extra:
            errors.append(f'Unknown request IDs ({len(extra)}): {list(extra)[:5]}')

    if len(df['request_id'].unique()) != len(df):
        errors.append('Duplicate request IDs found in output!')

    req_map = requests_df.set_index('request_id').to_dict(orient='index')

    for idx, row in df.iterrows():
        rid = row['request_id']
        if rid not in req_map:
            continue
            
        r_info = req_map[rid]
        req_amt = float(r_info['requested_amount'])
        req_date = str(r_info['request_date'])
        req_deadline = str(r_info['desired_completion_date'])
        allows_partial = bool(r_info.get('allows_partial_payment', True))
        
        # 3. amount_safe_to_pay bounds
        try:
            safe = float(row['amount_safe_to_pay'])
            if safe < -1e-6 or safe > req_amt + 1e-6:
                errors.append(f'{rid}: amount_safe_to_pay {safe} violates [0, {req_amt}]')
        except Exception:
            raw_val = str(row['amount_safe_to_pay'])
            errors.append(f'{rid}: invalid numeric amount_safe_to_pay: {raw_val}')

        # 4. Enums
        status = row['affordability_status']
        if status not in AFFORDABILITY_STATUSES:
            errors.append(f'{rid}: invalid affordability_status: {status}')

        method = row['recommended_payment_method']
        if method not in PAYMENT_METHODS:
            errors.append(f'{rid}: invalid recommended_payment_method: {method}')

        # 5. earliest_date_for_full_payment consistency
        earliest = str(row['earliest_date_for_full_payment']) if pd.notnull(row['earliest_date_for_full_payment']) else ''
        if status == 'affordable_now':
            if earliest != req_date:
                errors.append(f'{rid}: affordable_now requires earliest_date == request_date ({req_date}), got {earliest}')

        if status == 'not_affordable':
            if earliest != '' and earliest != 'nan':
                errors.append(f'{rid}: not_affordable requires empty earliest_date, got {earliest}')
            if row['payment_plan'] != 'none':
                plan_val = str(row['payment_plan'])
                errors.append(f'{rid}: not_affordable requires payment_plan none, got {plan_val}')

        # 6. Payment plan validation
        plan_str = str(row['payment_plan'])
        if plan_str != 'none' and plan_str != 'nan':
            parts = plan_str.split('|')
            last_date = ''
            for p in parts:
                p_tokens = p.split(':')
                if len(p_tokens) != 2:
                    errors.append(f'{rid}: malformed plan item format: {p}')
                    continue
                p_date, p_amt_str = p_tokens[0], p_tokens[1]
                if p_date < req_date:
                    errors.append(f'{rid}: plan date {p_date} before request_date {req_date}')
                if last_date and p_date < last_date:
                    errors.append(f'{rid}: plan dates not chronological ({last_date} -> {p_date})')
                last_date = p_date
            if last_date and last_date > req_deadline:
                errors.append(f'{rid}: plan last payment {last_date} exceeds completion deadline {req_deadline}')

        # 7. partial_payment consistency
        if method == 'partial_payment':
            if not allows_partial:
                errors.append(f'{rid}: partial_payment recommended when allows_partial_payment is False')
            plan = str(row['payment_plan'])
            parts = plan.split('|')
            if len(parts) != 2:
                errors.append(f'{rid}: partial_payment requires exactly 2 payments, got {len(parts)}')
            else:
                try:
                    p1_date, p1_amt_str = parts[0].split(':')
                    p2_date, p2_amt_str = parts[1].split(':')
                    p1_amt = float(p1_amt_str)
                    p2_amt = float(p2_amt_str)
                    if p1_date != req_date:
                        errors.append(f'{rid}: partial payment 1 date {p1_date} != request_date {req_date}')
                    if abs((p1_amt + p2_amt) - req_amt) > 0.05:
                        errors.append(f'{rid}: partial payments sum {p1_amt + p2_amt} != req_amt {req_amt}')
                except Exception as e:
                    errors.append(f'{rid}: error parsing partial plan {plan}: {e}')

        # 8. spending changes exclusivity
        changes = str(row['spending_changes_needed'])
        stop_ids = set()
        reduce_map = {}
        if changes != 'none' and pd.notnull(row['spending_changes_needed']) and changes != 'nan':
            c_parts = changes.split('|')
            if len(c_parts) > 3:
                errors.append(f'{rid}: too many spending changes ({len(c_parts)})')
            stopped = set()
            reduced = set()
            for c in c_parts:
                if c.startswith('stop:'):
                    ev_id = c.split(':')[1]
                    stopped.add(ev_id)
                    stop_ids.add(ev_id)
                elif c.startswith('reduce_to:'):
                    parts = c.split(':')
                    ev_id = parts[1]
                    amt_val = float(parts[2])
                    reduced.add(ev_id)
                    reduce_map[ev_id] = amt_val
            conflict = stopped.intersection(reduced)
            if conflict:
                errors.append(f'{rid}: mutually exclusive violation on {conflict}')

        # 9. Decision explanation non-empty check
        expl = str(row['decision_explanation']) if pd.notnull(row['decision_explanation']) else ''
        if not expl or len(expl.strip()) < 10:
            errors.append(f'{rid}: missing or overly brief decision_explanation')

    return len(errors) == 0, errors
