from typing import List, Optional
from code.models import PlanCandidate

def rank_plan_candidates(candidates: List[PlanCandidate]) -> Optional[PlanCandidate]:
    if not candidates:
        return None

    def plan_sort_key(c: PlanCandidate):
        # 1. Completes by desired deadline (True first -> 0 first)
        d_key = 0 if c.completes_by_deadline else 1
        # 2. Requires no spending changes (0 first)
        s_key = 0 if len(c.spending_changes) == 0 else 1
        # 3. Minimizes total amount paid
        amt_key = c.total_amount_paid
        # 4. Starts earlier
        start_key = c.start_date
        # 5. Fewer payments
        num_key = c.num_payments
        # 6. Lowest payment option ID (tie breaker)
        opt_key = c.payment_option_id or 'zzzzzzzz'
        return (d_key, s_key, amt_key, start_key, num_key, opt_key)

    ranked = sorted(candidates, key=plan_sort_key)
    return ranked[0]
