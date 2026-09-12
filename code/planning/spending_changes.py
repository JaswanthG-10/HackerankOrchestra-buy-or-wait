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

    # Identify eligible flexible events from history
    stop_cats = set(profile.expense_categories_user_is_willing_to_stop)
    reduce_cats = set(profile.expense_categories_user_is_willing_to_reduce)

    # Find the most recent event for each recurring flexible description
    history = [e for e in events if e.event_date <= request.request_date and e.status == 'settled']
    eligible_stops = {}
    eligible_reduces = {}

    for e in reversed(history):
        if e.direction == 'debit':
            # Check stoppable
            if e.category in stop_cats and e.flexibility in ['stoppable', 'reducible_or_stoppable']:
                if e.description not in eligible_stops:
                    eligible_stops[e.description] = e
            # Check reducible
            if e.category in reduce_cats and e.flexibility in ['reducible', 'reducible_or_stoppable']:
                if e.description not in eligible_reduces and e.minimum_allowed_amount is not None:
                    eligible_reduces[e.description] = e

    stop_list = list(eligible_stops.values())
    reduce_list = list(eligible_reduces.values())

    # Build candidate change sets (up to 3 changes)
    candidate_combos = []

    # 1 change: single stop
    for s in stop_list:
        candidate_combos.append(({s.event_id}, {}, [f'stop:{s.event_id}']))

    # 1 change: single reduce
    for r in reduce_list:
        amt_str = format_amount(r.minimum_allowed_amount)
        candidate_combos.append((set(), {r.event_id: r.minimum_allowed_amount}, [f'reduce_to:{r.event_id}:{amt_str}']))

    # 2 changes: stop + reduce (different events)
    for s in stop_list:
        for r in reduce_list:
            if s.event_id != r.event_id:
                amt_str = format_amount(r.minimum_allowed_amount)
                candidate_combos.append(({s.event_id}, {r.event_id: r.minimum_allowed_amount}, [f'stop:{s.event_id}', f'reduce_to:{r.event_id}:{amt_str}']))

    # 2 changes: two stops
    for i in range(len(stop_list)):
        for j in range(i + 1, len(stop_list)):
            candidate_combos.append(({stop_list[i].event_id, stop_list[j].event_id}, {}, [f'stop:{stop_list[i].event_id}', f'stop:{stop_list[j].event_id}']))

    # Test each combination
    full_schedule = [(request.request_date, request.requested_amount)]
    for stop_ids, reduce_map, change_strings in candidate_combos:
        _, headroom = run_90_day_simulation(
            profile=profile,
            events=events,
            resolved_info=resolved_info,
            request_date=request.request_date,
            stop_event_ids=stop_ids,
            reduce_event_map=reduce_map,
            payment_schedule=full_schedule
        )
        if headroom >= 0.0:
            p_str = format_amount(request.requested_amount)
            return PlanCandidate(
                method='full_payment',
                affordability_status='affordable_with_plan',
                payment_plan=f'{request.request_date}:{p_str}',
                schedule=full_schedule,
                completes_by_deadline=True,
                spending_changes=change_strings,
                total_amount_paid=request.requested_amount,
                start_date=request.request_date,
                num_payments=1,
                payment_option_id=None,
                is_safe=True
            )

    return None
