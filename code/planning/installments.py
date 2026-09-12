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

        # Check max installment months
        freq = opt.payment_frequency_days or 30.0
        duration_months = (opt.number_of_payments * freq) / 30.0
        if profile.max_installment_months is not None:
            if opt.number_of_payments > profile.max_installment_months and duration_months > profile.max_installment_months:
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
        completes_by_deadline = (last_pay_date <= request.desired_completion_date)

        # Run 90-day simulation
        _, headroom = run_90_day_simulation(
            profile=profile,
            events=events,
            resolved_info=resolved_info,
            request_date=request.request_date,
            payment_schedule=schedule
        )

        if headroom >= 0.0:
            candidates.append(PlanCandidate(
                method='installments',
                affordability_status='affordable_with_plan',
                payment_plan=plan_str,
                schedule=schedule,
                completes_by_deadline=completes_by_deadline,
                spending_changes=[],
                total_amount_paid=opt.total_payable_amount,
                start_date=opt.first_payment_date,
                num_payments=opt.number_of_payments,
                payment_option_id=opt.payment_option_id,
                is_safe=True
            ))

    return candidates
