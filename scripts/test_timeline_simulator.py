import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

from code.models import FinancialEvent, UserProfile
from code.finance.lifecycle import resolve_event_chains
from code.finance.recurrence import detect_recurring_obligations, RecurringObligation
from code.finance.salary import resolve_salary_plan

def simulate_user_90_days(
    profile: UserProfile,
    raw_events: List[FinancialEvent],
    user_messages: List[dict],
    request_date: str,
    stop_event_ids: Optional[Set[str]] = None,
    reduce_event_map: Optional[Dict[str, float]] = None,
    payment_schedule: Optional[List[Tuple[str, float]]] = None
) -> Tuple[List[Tuple[str, float]], float, str]:
    stop_event_ids = stop_event_ids or set()
    reduce_event_map = reduce_event_map or {}
    payment_schedule = payment_schedule or []
    
    req_dt = datetime.strptime(request_date, "%Y-%m-%d")
    end_dt = req_dt + timedelta(days=90)
    end_date_str = end_dt.strftime("%Y-%m-%d")
    
    # 1. Resolve lifecycle chains
    events = resolve_event_chains(raw_events)
    
    # 2. Inferred recurring obligations from settled history
    recurring_obs = detect_recurring_obligations(events, request_date)
    
    # 3. Resolve salary plan
    salary_info = resolve_salary_plan(profile, events, user_messages, request_date)
    
    # 4. Gather explicit future events from dataset
    # Rule: pending credits excluded; pending debits reserved; scheduled applied
    future_explicit = [
        e for e in events 
        if e.settlement_date >= request_date and e.settlement_date <= end_date_str
        and (e.status == "scheduled" or (e.status == "pending" and e.direction == "debit"))
    ]
    
    # Build timeline: map date -> list of (amount, direction, description)
    timeline: Dict[str, List[Tuple[float, str, str]]] = {}
    
    # A. Add explicit future events
    explicit_covered_keys = set() # (category, date)
    for fe in future_explicit:
        timeline.setdefault(fe.settlement_date, []).append((fe.amount, fe.direction, fe.description))
        explicit_covered_keys.add((fe.category, fe.settlement_date))
        
    # B. Add confirmed invoices
    for inv in salary_info.get("confirmed_invoices", []):
        timeline.setdefault(inv["date"], []).append((inv["amount"], "credit", "Confirmed invoice"))
        
    # C. Add future salary credits
    if not salary_info.get("salary_ended"):
        sal_day = salary_info["perm_sal_day"]
        base_sal_amt = salary_info["perm_sal_amount"]
        next_sal_amt = salary_info.get("next_sal_amount")
        next_sal_date = salary_info.get("next_sal_date")
        one_time_arr = salary_info.get("one_time_arrears", 0.0)
        first_sal_dt = salary_info.get("first_sal_date")
        
        # Determine all salary payment dates in the 90-day window
        first_cycle_done = False
        for d in range(91):
            cur_dt = req_dt + timedelta(days=d)
            cur_str = cur_dt.strftime("%Y-%m-%d")
            
            # Check if this date is the salary date
            is_sal_date = False
            if next_sal_date and not first_cycle_done:
                if cur_str == next_sal_date:
                    is_sal_date = True
            elif first_sal_dt:
                if cur_str == first_sal_dt or (cur_dt > datetime.strptime(first_sal_dt, "%Y-%m-%d") and cur_dt.day == sal_day):
                    is_sal_date = True
            elif cur_dt.day == sal_day:
                is_sal_date = True
                
            if is_sal_date:
                # Deduplicate if explicit salary already exists on this date
                if ("salary", cur_str) in explicit_covered_keys:
                    first_cycle_done = True
                    continue
                    
                cur_sal = base_sal_amt
                if not first_cycle_done and next_sal_amt is not None:
                    cur_sal = next_sal_amt
                if not first_cycle_done and one_time_arr > 0:
                    cur_sal += one_time_arr
                    
                if cur_sal > 0:
                    timeline.setdefault(cur_str, []).append((cur_sal, "credit", "Monthly salary"))
                first_cycle_done = True
                
    # D. Add recurring obligations
    # For weekly / biweekly / monthly
    for ob in recurring_obs:
        # Check spending changes
        if ob.event_id and ob.event_id in stop_event_ids:
            continue
        amt = ob.amount
        if ob.event_id and ob.event_id in reduce_event_map:
            amt = reduce_event_map[ob.event_id]
            
        if ob.frequency == "monthly" and ob.day_of_month is not None:
            for d in range(91):
                cur_dt = req_dt + timedelta(days=d)
                cur_str = cur_dt.strftime("%Y-%m-%d")
                if cur_dt.day == ob.day_of_month:
                    # Check deduplication with explicit events within +/- 2 days
                    is_dup = False
                    for offset in [-2, -1, 0, 1, 2]:
                        check_str = (cur_dt + timedelta(days=offset)).strftime("%Y-%m-%d")
                        if (ob.category, check_str) in explicit_covered_keys:
                            is_dup = True
                            break
                    if not is_dup:
                        timeline.setdefault(cur_str, []).append((amt, "debit", ob.description))
        elif ob.frequency == "weekly" and ob.day_of_week is not None:
            for d in range(91):
                cur_dt = req_dt + timedelta(days=d)
                cur_str = cur_dt.strftime("%Y-%m-%d")
                if cur_dt.weekday() == ob.day_of_week:
                    timeline.setdefault(cur_str, []).append((amt, "debit", ob.description))
        elif ob.frequency == "biweekly" and ob.last_date:
            last_dt = datetime.strptime(ob.last_date, "%Y-%m-%d")
            for d in range(91):
                cur_dt = req_dt + timedelta(days=d)
                cur_str = cur_dt.strftime("%Y-%m-%d")
                days_since = (cur_dt - last_dt).days
                if days_since > 0 and days_since % 14 == 0:
                    timeline.setdefault(cur_str, []).append((amt, "debit", ob.description))

    # E. Add extra purchase payment schedule
    for p_dt, p_amt in payment_schedule:
        timeline.setdefault(p_dt, []).append((p_amt, "debit", "Purchase payment"))
        
    # 5. Execute step-by-step chronological simulation
    curr_bal = profile.current_available_balance
    trajectory = []
    min_headroom = float("inf")
    min_date = request_date
    
    for d in range(91):
        cur_dt = req_dt + timedelta(days=d)
        cur_str = cur_dt.strftime("%Y-%m-%d")
        
        # Apply credits first, then debits
        day_entries = timeline.get(cur_str, [])
        credits = sum(item[0] for item in day_entries if item[1] == "credit")
        debits = sum(item[0] for item in day_entries if item[1] == "debit")
        
        curr_bal += credits
        curr_bal -= debits
        
        headroom = curr_bal - profile.minimum_balance_to_keep
        if headroom < min_headroom:
            min_headroom = headroom
            min_date = cur_str
            
        trajectory.append((cur_str, curr_bal))
        
    return trajectory, min_headroom, min_date

print("simulate_user_90_days defined successfully")
