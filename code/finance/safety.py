from datetime import datetime, timedelta
from typing import List, Optional
from code.models import UserProfile, FinancialEvent
from code.finance.forecast import run_90_day_simulation
from code.config import SAFE_TOLERANCE

def is_financially_safe(min_headroom: float) -> bool:
    """Canonical definition of financial safety: min_headroom >= SAFE_TOLERANCE (-0.05)."""
    return min_headroom >= SAFE_TOLERANCE

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
    amount_safe_to_pay: Optional[float] = None
) -> Optional[str]:
    """
    Finds the earliest date (from request_date up to request_date + 90 days) where
    paying requested_amount in full maintains minimum balance across the 90-day simulation.
    """
    req_dt = datetime.strptime(request_date, '%Y-%m-%d')
    for day_offset in range(0, 91):
        test_dt = req_dt + timedelta(days=day_offset)
        test_date_str = test_dt.strftime('%Y-%m-%d')

        _, test_headroom = run_90_day_simulation(
            profile=profile,
            events=events,
            resolved_info=resolved_info,
            request_date=request_date,
            payment_schedule=[(test_date_str, requested_amount)]
        )

        if is_financially_safe(test_headroom):
            return test_date_str

    return None
