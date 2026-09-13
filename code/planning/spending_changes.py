from datetime import datetime, timedelta
from itertools import combinations
from typing import Dict, List, Optional, Set, Tuple
from code.models import UserProfile, FinancialEvent, RequestItem, PlanCandidate
from code.finance.forecast import run_90_day_simulation
from code.config import format_amount

def evaluate_spending_changes(
    profile: UserProfile,
    events: List[FinancialEvent],
    resolved_info: dict,
    request: RequestItem,
    amount_safe_to_pay: float
) -> Optional[PlanCandidate]:
    if 'full_payment' not in profile.payment_methods_user_will_consider:
        return None

    stop_cats = set(profile.expense_categories_user_is_willing_to_stop)
    reduce_cats = set(profile.expense_categories_user_is_willing_to_reduce)

    # Detect recurring obligations to ensure candidates are genuinely recurring
    from code.finance.recurrence import detect_recurring_obligations
    rec_obs = detect_recurring_obligations(events, request.request_date)
    rec_descs = set(r.description for r in rec_obs)
    rec_event_ids = set(r.event_id for r in rec_obs if r.event_id)

    # Find the most recent event for each recurring flexible description
    history = [e for e in events if e.event_date <= request.request_date and e.status == 'settled']
    eligible_stops = {}
    eligible_reduces = {}

    for e in reversed(history):
        if e.direction == 'debit' and (e.event_id in rec_event_ids or e.description in rec_descs):
            if e.category in stop_cats and e.flexibility in ['stoppable', 'reducible_or_stoppable']:
                if e.description not in eligible_stops:
                    eligible_stops[e.description] = e
            if e.category in reduce_cats and e.flexibility in ['reducible', 'reducible_or_stoppable']:
                if e.description not in eligible_reduces and e.minimum_allowed_amount is not None:
                    eligible_reduces[e.description] = e

    stop_list = list(eligible_stops.values())
    reduce_list = list(eligible_reduces.values())

    # Build candidate change sets (up to 3 changes)
    candidate_combos = []

    # 1 change: single stop
    for s in stop_list:
        candidate_combos.append(({s.event_id}, {}, [s], []))

    # 1 change: single reduce
    for r in reduce_list:
        candidate_combos.append((set(), {r.event_id: r.minimum_allowed_amount}, [], [r]))

    # 2 changes: stop + reduce (different events)
    for s in stop_list:
        for r in reduce_list:
            if s.event_id != r.event_id:
                candidate_combos.append(({s.event_id}, {r.event_id: r.minimum_allowed_amount}, [s], [r]))

    # 2 changes: two stops
    for s1, s2 in combinations(stop_list, 2):
        candidate_combos.append(({s1.event_id, s2.event_id}, {}, [s1, s2], []))

    # 2 changes: two reduces
    for r1, r2 in combinations(reduce_list, 2):
        candidate_combos.append((set(), {r1.event_id: r1.minimum_allowed_amount, r2.event_id: r2.minimum_allowed_amount}, [], [r1, r2]))

    # 3 changes: 3 stops
    for s1, s2, s3 in combinations(stop_list, 3):
        candidate_combos.append(({s1.event_id, s2.event_id, s3.event_id}, {}, [s1, s2, s3], []))

    # 3 changes: 2 stops + 1 reduce
    for s1, s2 in combinations(stop_list, 2):
        for r in reduce_list:
            if r.event_id not in [s1.event_id, s2.event_id]:
                candidate_combos.append(({s1.event_id, s2.event_id}, {r.event_id: r.minimum_allowed_amount}, [s1, s2], [r]))

    # 3 changes: 1 stop + 2 reduces
    for s in stop_list:
        for r1, r2 in combinations(reduce_list, 2):
            if s.event_id not in [r1.event_id, r2.event_id]:
                candidate_combos.append(({s.event_id}, {r1.event_id: r1.minimum_allowed_amount, r2.event_id: r2.minimum_allowed_amount}, [s], [r1, r2]))

    # 3 changes: 3 reduces
    for r1, r2, r3 in combinations(reduce_list, 3):
        candidate_combos.append((set(), {r.event_id: r.minimum_allowed_amount for r in [r1, r2, r3]}, [], [r1, r2, r3]))

    req_dt = datetime.strptime(request.request_date, '%Y-%m-%d')
    end_dt = datetime.strptime(request.desired_completion_date, '%Y-%m-%d')
    cand_dates = [request.request_date]
    max_days = min(90, (end_dt - req_dt).days)
    for d in range(1, max_days + 1):
        cdt = req_dt + timedelta(days=d)
        if cdt.day in [1, 15]:
            cand_dates.append(cdt.strftime('%Y-%m-%d'))

    # Sort combos by total changes count (prefer 1 change, then 2, then 3)
    candidate_combos.sort(key=lambda c: len(c[2]) + len(c[3]))

    for cand_date in cand_dates:
        full_schedule = [(cand_date, request.requested_amount)]
        for stop_ids, reduce_map, s_objs, r_objs in candidate_combos:
            # First test if combo works with maximum reduction
            _, headroom = run_90_day_simulation(
                profile=profile,
                events=events,
                resolved_info=resolved_info,
                request_date=request.request_date,
                stop_event_ids=stop_ids,
                reduce_event_map=reduce_map,
                payment_schedule=full_schedule
            )
            if headroom >= -0.05:
                # Issue 14: Find minimum necessary reduction!
                final_reduce_map = dict(reduce_map)
                for r in r_objs:
                    min_amt = r.minimum_allowed_amount
                    max_amt = r.amount
                    low = min_amt
                    high = max_amt
                    best_amt = min_amt
                    
                    for step in range(12):
                        mid = (low + high) / 2.0
                        test_map = dict(final_reduce_map)
                        test_map[r.event_id] = round(mid, 2)
                        _, test_hd = run_90_day_simulation(
                            profile=profile,
                            events=events,
                            resolved_info=resolved_info,
                            request_date=request.request_date,
                            stop_event_ids=stop_ids,
                            reduce_event_map=test_map,
                            payment_schedule=full_schedule
                        )
                        if test_hd >= -0.05:
                            best_amt = round(mid, 2)
                            low = mid
                        else:
                            high = mid
                            
                    final_reduce_map[r.event_id] = best_amt

                # Build formatted change strings
                change_strings = []
                for s in s_objs:
                    change_strings.append(f'stop:{s.event_id}')
                for r in r_objs:
                    amt_val = final_reduce_map[r.event_id]
                    amt_str = format_amount(amt_val)
                    change_strings.append(f'reduce_to:{r.event_id}:{amt_str}')

                p_str = format_amount(request.requested_amount)
                return PlanCandidate(
                    method='full_payment',
                    affordability_status='affordable_with_plan',
                    payment_plan=f'{cand_date}:{p_str}',
                    schedule=full_schedule,
                    completes_by_deadline=True,
                    spending_changes=change_strings,
                    total_amount_paid=request.requested_amount,
                    start_date=cand_date,
                    num_payments=1,
                    payment_option_id=None,
                    is_safe=True
                )

    return None
