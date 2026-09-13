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

    # 2. Row count
    if len(df) != len(requests_df):
        errors.append(f'Row count mismatch! Expected {len(requests_df)}, Got {len(df)}')

    req_map = requests_df.set_index('request_id').to_dict(orient='index')

    for idx, row in df.iterrows():
        rid = row['request_id']
        if rid not in req_map:
            errors.append(f'Unknown request_id: {rid}')
            continue
            
        r_info = req_map[rid]
        req_amt = float(r_info['requested_amount'])
        req_date = str(r_info['request_date'])
        
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

        # 6. partial_payment consistency
        if method == 'partial_payment':
            plan = str(row['payment_plan'])
            parts = plan.split('|')
            if len(parts) != 2:
                errors.append(f'{rid}: partial_payment requires exactly 2 payments, got {len(parts)}')
            else:
                try:
                    p1_amt = float(parts[0].split(':')[1])
                    p2_amt = float(parts[1].split(':')[1])
                    if abs((p1_amt + p2_amt) - req_amt) > 0.05:
                        errors.append(f'{rid}: partial payments sum {p1_amt + p2_amt} != req_amt {req_amt}')
                except Exception as e:
                    errors.append(f'{rid}: error parsing partial plan {plan}: {e}')

        # 7. spending changes exclusivity
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

        # 8. Decision explanation non-empty check
        expl = str(row['decision_explanation']) if pd.notnull(row['decision_explanation']) else ''
        if not expl or len(expl.strip()) < 10:
            errors.append(f'{rid}: missing or overly brief decision_explanation')

    return len(errors) == 0, errors
