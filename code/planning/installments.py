from datetime import datetime, timedelta
from typing import List, Optional
from code.models import UserProfile, FinancialEvent, PaymentOption, RequestItem, PlanCandidate
from code.finance.forecast import run_90_day_simulation
from code.config import format_amount

def evaluate_installment_options(
    profile: UserProfile,
    events: List[FinancialEvent],
    resolved_info: dict,
    request: RequestItem,
    options: List[PaymentOption]
) -> List[PlanCandidate]:
    candidates = []
    if 'installments' not in profile.payment_methods_user_will_consider:
        return candidates

    for opt in options:
        if opt.payment_method != 'installments':
            continue

        freq = opt.payment_frequency_days or 30.0
        
        # Duration check (Issue 10):
        # actual plan duration in days = (number_of_payments - 1) * freq
        duration_days = (opt.number_of_payments - 1) * freq
        duration_months = duration_days / 30.0
        if profile.max_installment_months is not None:
            if duration_months > profile.max_installment_months:
                continue

        # Build schedule
        start_dt = datetime.strptime(opt.first_payment_date, '%Y-%m-%d')
        schedule = []
        plan_parts = []
        for i in range(opt.number_of_payments):
            pay_dt = start_dt + timedelta(days=int(i * freq))
            pay_str = pay_dt.strftime('%Y-%m-%d')
            schedule.append((pay_str, opt.payment_amount))
            amt_str = format_amount(opt.payment_amount)
            plan_parts.append(f'{pay_str}:{amt_str}')

        plan_str = '|'.join(plan_parts)
        last_pay_date = schedule[-1][0]
        
        # Deadline check (Issue 9):
        # A plan that does not complete by requested deadline is strictly ineligible!
        if last_pay_date > request.desired_completion_date:
            continue

        # Run 90-day simulation
        _, headroom = run_90_day_simulation(
            profile=profile,
            events=events,
            resolved_info=resolved_info,
            request_date=request.request_date,
            payment_schedule=schedule
        )

        if headroom >= -0.05:
            candidates.append(PlanCandidate(
                method='installments',
                affordability_status='affordable_with_plan',
                payment_plan=plan_str,
                schedule=schedule,
                completes_by_deadline=True,
                spending_changes=[],
                total_amount_paid=opt.total_payable_amount,
                start_date=opt.first_payment_date,
                num_payments=opt.number_of_payments,
                payment_option_id=opt.payment_option_id,
                is_safe=True
            ))

    return candidates
