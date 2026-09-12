import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

from code.loader import load_profiles, load_exchange_rates, load_image_cache, load_financial_events, load_requests, load_message_cache
from code.finance.lifecycle import resolve_event_chains
from code.finance.salary import resolve_salary_plan
from code.models import FinancialEvent, UserProfile

def simulate_accurate(
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
    
    events = resolve_event_chains(raw_events)
    history = [e for e in events if e.event_date <= request_date and e.status == "settled" and e.direction == "debit"]
    
    # Categories to forecast:
    # 1. All fixed categories / subscriptions
    fixed_cats = {
        "rent", "utilities", "debt_repayment", "education", "insurance",
        "family_support", "healthcare", "housing", "cloud_storage",
        "streaming", "delivery_membership", "gym", "music_subscription"
    }
    # 2. Protected categories
    protected_cats = set(profile.expense_categories_to_protect or [])
    
    # Identify recurring obligations from history
    # Group by description
    desc_groups: Dict[str, List[FinancialEvent]] = {}
    for e in history:
        desc_groups.setdefault(e.description, []).append(e)
        
    recurring_items = []
    
    for desc, evs in desc_groups.items():
        evs.sort(key=lambda x: x.event_date)
        last_ev = evs[-1]
        cat = last_ev.category
        
        # Only include if fixed category OR in protected categories OR is stoppable/reducible
        is_fixed = cat in fixed_cats or last_ev.event_type in ["subscription", "debt_payment"]
        is_protected = cat in protected_cats
        is_flexible = last_ev.flexibility in ["stoppable", "reducible", "reducible_or_stoppable"]
        
        if not (is_fixed or is_protected or is_flexible):
            continue
            
        dates = [datetime.strptime(e.event_date, "%Y-%m-%d") for e in evs]
        deltas = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        med_delta = float(np.median(deltas)) if deltas else 30.0
        
        recent_amts = [e.amount for e in evs[-3:]]
        amount = float(np.median(recent_amts))
        
        # Determine schedule
        frequency = "monthly"
        dom = dates[-1].day
        dow = None
        
        if 6.0 <= med_delta <= 8.5:
            frequency = "weekly"
            dow = dates[-1].weekday()
        elif 13.0 <= med_delta <= 16.5:
            frequency = "biweekly"
            dow = dates[-1].weekday()
        else:
            from collections import Counter
            days = [d.day for d in dates]
            dom = Counter(days).most_common(1)[0][0]
            
        recurring_items.append({
            "description": desc,
            "category": cat,
            "amount": amount,
            "frequency": frequency,
            "day_of_month": dom,
            "day_of_week": dow,
            "last_date": evs[-1].event_date,
            "event_id": last_ev.event_id,
            "flexibility": last_ev.flexibility,
            "minimum_allowed_amount": last_ev.minimum_allowed_amount
        })
        
    salary_info = resolve_salary_plan(profile, events, user_messages, request_date)
    
    future_explicit = [
        e for e in events 
        if e.settlement_date >= request_date and e.settlement_date <= end_date_str
        and (e.status == "scheduled" or (e.status == "pending" and e.direction == "debit"))
    ]
    
    timeline: Dict[str, List[Tuple[float, str, str]]] = {}
    explicit_covered_keys = set()
    for fe in future_explicit:
        timeline.setdefault(fe.settlement_date, []).append((fe.amount, fe.direction, fe.description))
        explicit_covered_keys.add((fe.category, fe.settlement_date))
        
    for inv in salary_info.get("confirmed_invoices", []):
        timeline.setdefault(inv["date"], []).append((inv["amount"], "credit", "Confirmed invoice"))
        
    if not salary_info.get("salary_ended"):
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
                
    for item in recurring_items:
        ev_id = item["event_id"]
        if ev_id and ev_id in stop_event_ids:
            continue
        amt = item["amount"]
        if ev_id and ev_id in reduce_event_map:
            amt = reduce_event_map[ev_id]
            
        if item["frequency"] == "monthly":
            dom = item["day_of_month"]
            for d in range(91):
                cur_dt = req_dt + timedelta(days=d)
                cur_str = cur_dt.strftime("%Y-%m-%d")
                if cur_dt.day == dom:
                    is_dup = any((item["category"], (cur_dt + timedelta(days=off)).strftime("%Y-%m-%d")) in explicit_covered_keys for off in [-2, -1, 0, 1, 2])
                    if not is_dup:
                        timeline.setdefault(cur_str, []).append((amt, "debit", item["description"]))
        elif item["frequency"] == "weekly":
            dow = item["day_of_week"]
            for d in range(91):
                cur_dt = req_dt + timedelta(days=d)
                cur_str = cur_dt.strftime("%Y-%m-%d")
                if cur_dt.weekday() == dow:
                    timeline.setdefault(cur_str, []).append((amt, "debit", item["description"]))
        elif item["frequency"] == "biweekly":
            last_dt = datetime.strptime(item["last_date"], "%Y-%m-%d")
            for d in range(91):
                cur_dt = req_dt + timedelta(days=d)
                cur_str = cur_dt.strftime("%Y-%m-%d")
                if (cur_dt - last_dt).days > 0 and (cur_dt - last_dt).days % 14 == 0:
                    timeline.setdefault(cur_str, []).append((amt, "debit", item["description"]))
                    
    for p_dt, p_amt in payment_schedule:
        timeline.setdefault(p_dt, []).append((p_amt, "debit", "Purchase payment"))
        
    curr_bal = profile.current_available_balance
    trajectory = []
    min_headroom = float("inf")
    min_date = request_date
    
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
            min_date = cur_str
        trajectory.append((cur_str, curr_bal))
        
    return trajectory, min_headroom, min_date

print("Defined simulate_accurate successfully")
