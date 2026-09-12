from datetime import datetime, timedelta
from typing import List, Optional
from code.models import UserProfile, FinancialEvent
from code.finance.forecast import run_90_day_simulation

def compute_amount_safe_to_pay(
    profile: UserProfile,
    events: List[FinancialEvent],
    resolved_info: dict,
    request_date: str,
    requested_amount: float
) -> float:
    _, min_headroom = run_90_day_simulation(
        profile=profile,
        events=events,
        resolved_info=resolved_info,
        request_date=request_date
    )
    safe_amt = max(0.0, min(requested_amount, min_headroom))
    return round(safe_amt, 2)

def compute_earliest_date_for_full_payment(
    profile: UserProfile,
    events: List[FinancialEvent],
    resolved_info: dict,
    request_date: str,
    requested_amount: float,
    amount_safe_to_pay: float
) -> Optional[str]:
    # If safe today, earliest date is today
    if amount_safe_to_pay >= requested_amount:
        return request_date

    req_dt = datetime.strptime(request_date, '%Y-%m-%d')
    trajectory, _ = run_90_day_simulation(
        profile=profile,
        events=events,
        resolved_info=resolved_info,
        request_date=request_date
    )

    # Test candidate dates (prioritizing salary dates and days when balance surges)
    for day_offset in range(1, 90):
        test_dt = req_dt + timedelta(days=day_offset)
        test_date_str = test_dt.strftime('%Y-%m-%d')

        # Run simulation with full payment on test_date_str
        _, test_headroom = run_90_day_simulation(
            profile=profile,
            events=events,
            resolved_info=resolved_info,
            request_date=request_date,
            payment_schedule=[(test_date_str, requested_amount)]
        )

        if test_headroom >= 0.0:
            return test_date_str

    return None
