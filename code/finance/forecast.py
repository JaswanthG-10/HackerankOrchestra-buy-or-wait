from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set

from code.models import UserProfile, FinancialEvent, RequestItem
from code.finance.lifecycle import resolve_event_chains
from code.finance.recurrence import detect_recurring_obligations, RecurringObligation
from code.finance.salary import resolve_salary_plan

def build_forecast_timeline(
    profile: UserProfile,
    events: List[FinancialEvent],
    resolved_info: dict,
    request_date: str,
    stop_event_ids: Optional[Set[str]] = None,
    reduce_event_map: Optional[Dict[str, float]] = None,
    payment_schedule: Optional[List[Tuple[str, float]]] = None
) -> Dict[str, List[Tuple[float, str, str]]]:
    stop_event_ids = stop_event_ids or set()
    reduce_event_map = reduce_event_map or {}
    payment_schedule = payment_schedule or []
    
    req_dt = datetime.strptime(request_date, "%Y-%m-%d")
    end_dt = req_dt + timedelta(days=90)
    end_date_str = end_dt.strftime("%Y-%m-%d")
    
    # 1. Resolve event lifecycles
    clean_events = resolve_event_chains(events)
    
    # 2. Inferred recurring obligations
    recurring_obs = detect_recurring_obligations(clean_events, request_date)
    
    # 3. User messages & salary info
    user_msgs = resolved_info.get("messages", [])
    salary_info = resolve_salary_plan(profile, clean_events, user_msgs, request_date)
    
    # 4. Explicit future events from dataset
    # Rules: pending credits excluded; pending debits reserved; scheduled debits/credits applied
    explicit_covered_keys = set() # (category, date)
    timeline: Dict[str, List[Tuple[float, str, str]]] = {}
    
    for e in clean_events:
        if e.status == "scheduled" and e.settlement_date >= request_date and e.settlement_date <= end_date_str:
            timeline.setdefault(e.settlement_date, []).append((e.amount, e.direction, e.description))
            explicit_covered_keys.add((e.category, e.settlement_date))
        elif e.status == "pending" and e.direction == "debit":
            # Reserve pending debit
            # If settlement date is in the future, debit on settlement date
            # If settlement date <= request date, debit on day 0 (today)
            apply_date = e.settlement_date if e.settlement_date >= request_date else request_date
            if apply_date <= end_date_str:
                timeline.setdefault(apply_date, []).append((e.amount, "debit", f"Pending debit reserve: {e.description}"))
                explicit_covered_keys.add((e.category, apply_date))
                
    # 5. Add confirmed invoices
    for inv in salary_info.get("confirmed_invoices", []):
        if inv["date"] >= request_date and inv["date"] <= end_date_str:
            timeline.setdefault(inv["date"], []).append((inv["amount"], "credit", "Confirmed invoice"))
            
    # 6. Add forward salary schedule
    next_sal_date_str = None
    if not salary_info.get("salary_ended") and not salary_info.get("is_gig_worker"):
        sal_day = salary_info["perm_sal_day"]
        base_sal_amt = salary_info["perm_sal_amount"]
        next_sal_amt = salary_info.get("next_sal_amount")
        next_sal_date = salary_info.get("next_sal_date")
        one_time_arr = salary_info.get("one_time_arrears", 0.0)
        first_sal_dt = salary_info.get("first_sal_date")
        
        first_cycle_done = False
        for d in range(91):
            cur_dt = req_dt + timedelta(days=d)
            cur_str = cur_dt.strftime("%Y-%m-%d")
            
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
                if not next_sal_date_str:
                    next_sal_date_str = cur_str
                # Deduplicate if explicit scheduled salary already exists in dataset on this date
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

    # 7. Add recurring obligations with variable category budget normalization
    history_debits = [e for e in clean_events if e.event_date <= request_date and e.status == 'settled' and e.direction == 'debit']
    m_counts = len(set(e.event_date[:7] for e in history_debits))
    cat_hist_avg = {}
    for e in history_debits:
        cat_hist_avg[e.category] = cat_hist_avg.get(e.category, 0.0) + e.amount / max(1, m_counts)
        
    rec_monthly = {}
    for r in recurring_obs:
        mult = 4.33 if r.frequency == 'weekly' else (2.17 if r.frequency == 'biweekly' else (1.43 if r.frequency == 'every_21_days' else 1.0))
        rec_monthly[r.category] = rec_monthly.get(r.category, 0.0) + r.amount * mult

    for ob in recurring_obs:
        # Check spending changes
        if ob.event_id and ob.event_id in stop_event_ids:
            continue
        amt = ob.amount
        if ob.event_id and ob.event_id in reduce_event_map:
            amt = reduce_event_map[ob.event_id]
        elif ob.category in ['groceries', 'transport', 'dining', 'shopping'] and ob.flexibility == 'fixed':
            if ob.category in cat_hist_avg and rec_monthly.get(ob.category, 0.0) > cat_hist_avg[ob.category]:
                scale = cat_hist_avg[ob.category] / rec_monthly[ob.category]
                amt = ob.amount * scale
            
        if ob.frequency == "every_21_days" and ob.last_date:
            last_dt = datetime.strptime(ob.last_date, "%Y-%m-%d")
            step_dt = last_dt + timedelta(days=21)
            while step_dt <= end_dt:
                if step_dt >= req_dt:
                    cur_str = step_dt.strftime("%Y-%m-%d")
                    is_dup = any((ob.category, (step_dt + timedelta(days=off)).strftime("%Y-%m-%d")) in explicit_covered_keys for off in [-1, 0, 1])
                    if not is_dup:
                        timeline.setdefault(cur_str, []).append((amt, "debit", ob.description))
                step_dt += timedelta(days=21)
        elif ob.frequency == "monthly" and ob.day_of_month is not None:
            for d in range(91):
                cur_dt = req_dt + timedelta(days=d)
                cur_str = cur_dt.strftime("%Y-%m-%d")
                if cur_dt.day == ob.day_of_month:
                    # Check deduplication with explicit events within +/- 2 days
                    is_dup = any((ob.category, (cur_dt + timedelta(days=off)).strftime("%Y-%m-%d")) in explicit_covered_keys for off in [-2, -1, 0, 1, 2])
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
        elif ob.frequency == "every_21_days" and ob.last_date:
            last_dt = datetime.strptime(ob.last_date, "%Y-%m-%d")
            for d in range(91):
                cur_dt = req_dt + timedelta(days=d)
                cur_str = cur_dt.strftime("%Y-%m-%d")
                days_since = (cur_dt - last_dt).days
                if days_since > 0 and days_since % 21 == 0:
                    timeline.setdefault(cur_str, []).append((amt, "debit", ob.description))

    # Pre-payday living expenses check:
    # Ensure pre-payday balance accounts for normal active living expenses before first payday
    if next_sal_date_str:
        payday_dt = datetime.strptime(next_sal_date_str, "%Y-%m-%d")
        days_until_payday = (payday_dt - req_dt).days
        if 0 < days_until_payday <= 20:
            pre_payday_str = (payday_dt - timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Check all debit categories occurring before payday in current timeline
            debits_before = set()
            for d in range(days_until_payday):
                d_str = (req_dt + timedelta(days=d)).strftime("%Y-%m-%d")
                for entry in timeline.get(d_str, []):
                    if entry[1] == 'debit':
                        found_cat = None
                        for ob in recurring_obs:
                            if ob.description == entry[2]:
                                found_cat = ob.category
                                break
                        if not found_cat:
                            for e in clean_events:
                                if e.description == entry[2] or f"Pending debit reserve: {e.description}" == entry[2]:
                                    found_cat = e.category
                                    break
                        if found_cat:
                            debits_before.add(found_cat)
            
            for e in clean_events:
                if request_date <= e.settlement_date <= next_sal_date_str and e.direction == 'debit':
                    debits_before.add(e.category)
                                
            # For living categories that have no debit scheduled before payday:
            for cat in ['dining', 'transport', 'groceries']:
                if cat not in debits_before:
                    cat_evs = [e for e in clean_events if e.category == cat and e.event_date <= request_date and e.status == 'settled']
                    if cat_evs:
                        early_evs = [e for e in cat_evs if datetime.strptime(e.event_date, "%Y-%m-%d").day <= payday_dt.day]
                        last_e = early_evs[-1] if early_evs else cat_evs[-1]
                        amt = last_e.amount
                        if last_e.event_id in stop_event_ids:
                            continue
                        if last_e.event_id in reduce_event_map:
                            amt = reduce_event_map[last_e.event_id]
                        timeline.setdefault(pre_payday_str, []).append((amt, "debit", last_e.description))

    # 8. Extra purchase payment schedule
    for p_dt, p_amt in payment_schedule:
        timeline.setdefault(p_dt, []).append((p_amt, "debit", "Purchase payment"))
        
    return timeline

def run_90_day_simulation(
    profile: UserProfile,
    events: List[FinancialEvent],
    resolved_info: dict,
    request_date: str,
    stop_event_ids: Optional[Set[str]] = None,
    reduce_event_map: Optional[Dict[str, float]] = None,
    payment_schedule: Optional[List[Tuple[str, float]]] = None
) -> Tuple[List[Tuple[str, float]], float]:
    timeline = build_forecast_timeline(
        profile=profile,
        events=events,
        resolved_info=resolved_info,
        request_date=request_date,
        stop_event_ids=stop_event_ids,
        reduce_event_map=reduce_event_map,
        payment_schedule=payment_schedule
    )
    
    req_dt = datetime.strptime(request_date, "%Y-%m-%d")
    curr_bal = profile.current_available_balance
    trajectory = []
    min_headroom = float("inf")
    
    for d in range(91):
        cur_dt = req_dt + timedelta(days=d)
        cur_str = cur_dt.strftime("%Y-%m-%d")
        
        day_entries = timeline.get(cur_str, [])
        credits = sum(x[0] for x in day_entries if x[1] == "credit")
        debits = sum(x[0] for x in day_entries if x[1] == "debit")
        
        curr_bal += credits
        curr_bal -= debits
        
        hd = curr_bal - profile.minimum_balance_to_keep
        if hd < min_headroom:
            min_headroom = hd
            
        trajectory.append((cur_str, curr_bal))
        
    return trajectory, min_headroom

def find_earliest_safe_full_payment_date(
    profile: UserProfile,
    events: List[FinancialEvent],
    resolved_info: dict,
    request_date: str,
    requested_amount: float,
    desired_completion_date: str
) -> Optional[str]:
    """
    Finds the earliest date where paying requested_amount in full
    maintains balance >= minimum_balance_to_keep across the entire remaining 90 days.
    """
    req_dt = datetime.strptime(request_date, "%Y-%m-%d")
    end_dt = datetime.strptime(desired_completion_date, "%Y-%m-%d")
    max_days = min(90, (end_dt - req_dt).days)
    if max_days < 0:
        return None
        
    for d in range(max_days + 1):
        cand_dt = req_dt + timedelta(days=d)
        cand_str = cand_dt.strftime("%Y-%m-%d")
        
        _, hd = run_90_day_simulation(
            profile=profile,
            events=events,
            resolved_info=resolved_info,
            request_date=request_date,
            payment_schedule=[(cand_str, requested_amount)]
        )
        
        if hd >= 0.0:
            return cand_str
            
    return None
