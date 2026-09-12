from typing import Optional
from code.models import UserProfile, FinancialEvent, RequestItem, PlanCandidate
from code.finance.forecast import run_90_day_simulation
from code.config import format_amount

def evaluate_partial_payment(
    profile: UserProfile,
    events: list,
    resolved_info: dict,
    request: RequestItem,
    amount_safe_to_pay: float,
    earliest_date_for_full_payment: Optional[str]
) -> Optional[PlanCandidate]:
    # Check conditions
    if not request.allows_partial_payment:
        return None
    if 'partial_payment' not in profile.payment_methods_user_will_consider:
        return None
    if not (0 < amount_safe_to_pay < request.requested_amount):
        return None
    if not earliest_date_for_full_payment:
        return None
    if earliest_date_for_full_payment > request.desired_completion_date:
        return None

    rem_amount = round(request.requested_amount - amount_safe_to_pay, 2)
    schedule = [
        (request.request_date, amount_safe_to_pay),
        (earliest_date_for_full_payment, rem_amount)
    ]

    p1_str = format_amount(amount_safe_to_pay)
    p2_str = format_amount(rem_amount)
    plan_str = f'{request.request_date}:{p1_str}|{earliest_date_for_full_payment}:{p2_str}'

    # Simulation check
    _, headroom = run_90_day_simulation(
        profile=profile,
        events=events,
        resolved_info=resolved_info,
        request_date=request.request_date,
        payment_schedule=schedule
    )

    if headroom >= -0.05:
        return PlanCandidate(
            method='partial_payment',
            affordability_status='affordable_with_plan',
            payment_plan=plan_str,
            schedule=schedule,
            completes_by_deadline=True,
            spending_changes=[],
            total_amount_paid=request.requested_amount,
            start_date=request.request_date,
            num_payments=2,
            payment_option_id=None,
            is_safe=True
        )

    return None
