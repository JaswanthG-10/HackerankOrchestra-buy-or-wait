from datetime import datetime
from typing import Dict, List, Optional, Tuple
from code.models import FinancialEvent, UserProfile

def resolve_salary_plan(
    profile: UserProfile,
    events: List[FinancialEvent],
    user_messages: List[dict],
    request_date: str
) -> Dict[str, any]:
    """
    Builds the forward salary schedule:
    - Incorporates explicit scheduled future salary from events
    - Determines baseline recurring salary and pay day
    - Handles contract endings, temporary leaves, date changes, arrears, confirmed invoices
    """
    req_dt = datetime.strptime(request_date, "%Y-%m-%d")
    history = [e for e in events if e.event_date <= request_date and e.status == "settled"]
    
    # Check if user is freelance/gig worker
    is_gig_worker = False
    for e in history:
        if e.direction == "credit" and e.category == "salary":
            desc_lower = e.description.lower()
            if any(w in desc_lower for w in ["platform payout", "app earnings", "marketplace payout"]):
                is_gig_worker = True
                break

    # Check for explicit scheduled future salary event
    sched_sal = [
        e for e in events 
        if e.status == "scheduled" and e.category == "salary" and e.settlement_date >= request_date
    ]
    
    base_sal_amount = 0.0
    base_sal_day = 15
    if sched_sal:
        sched_sal.sort(key=lambda x: x.settlement_date)
        first_sched = sched_sal[0]
        base_sal_amount = first_sched.amount
        base_sal_day = datetime.strptime(first_sched.settlement_date, "%Y-%m-%d").day
    else:
        # Fall back to settled historical salary
        regular_sals = [
            e for e in history 
            if e.direction == "credit" and e.category == "salary"
            and not any(w in e.description.lower() for w in ["bonus", "arrears", "commission", "tax refund", "reimbursement"])
        ]
        if regular_sals:
            base_sal_amount = regular_sals[-1].amount
            from collections import Counter
            days = [datetime.strptime(e.settlement_date, "%Y-%m-%d").day for e in regular_sals]
            base_sal_day = Counter(days).most_common(1)[0][0]

    # Process message facts
    salary_ended = False
    perm_sal_amount = base_sal_amount
    perm_sal_day = base_sal_day
    next_sal_amount = None
    next_sal_date = None
    first_sal_date = None
    one_time_arrears = 0.0
    confirmed_invoices = []
    
    # Check if latest settled salary in history indicates final payroll
    settled_sals = [e for e in history if e.direction == "credit" and e.category == "salary"]
    if settled_sals and "final employer payroll" in settled_sals[-1].description.lower():
        salary_ended = True
        
    for msg in user_messages:
        fact_type = msg.get("fact_type")
        txt = str(msg.get("summary", "")).lower()
        
        if fact_type == "contract_ended":
            salary_ended = True
        elif fact_type == "pending_unconfirmed" and is_gig_worker:
            salary_ended = True
        elif fact_type == "salary_update":
            amt = msg.get("amount")
            eff_dt = msg.get("effective_date")
            if "unpaid leave" in txt or "next salary is reduced" in txt or "next payroll" in txt:
                next_sal_amount = float(amt) if amt is not None else None
            else:
                if amt is not None:
                    perm_sal_amount = float(amt)
                if eff_dt:
                    next_sal_date = eff_dt
                    perm_sal_day = datetime.strptime(next_sal_date, "%Y-%m-%d").day
        elif fact_type == "salary_date_change":
            if msg.get("effective_date"):
                next_sal_date = msg["effective_date"]
                perm_sal_day = datetime.strptime(next_sal_date, "%Y-%m-%d").day
        elif fact_type == "confirmed_income":
            if msg.get("amount") and msg.get("effective_date"):
                confirmed_invoices.append({
                    "amount": float(msg["amount"]),
                    "date": msg["effective_date"]
                })
        elif "first salary" in txt:
            if msg.get("amount"):
                perm_sal_amount = float(msg["amount"])
            if msg.get("effective_date"):
                first_sal_date = msg["effective_date"]
                perm_sal_day = datetime.strptime(first_sal_date, "%Y-%m-%d").day
        elif "arrears" in txt and msg.get("amount"):
            one_time_arrears = float(msg["amount"])

    return {
        "salary_ended": salary_ended,
        "base_sal_amount": base_sal_amount,
        "perm_sal_amount": perm_sal_amount,
        "perm_sal_day": perm_sal_day,
        "next_sal_amount": next_sal_amount,
        "next_sal_date": next_sal_date,
        "first_sal_date": first_sal_date,
        "one_time_arrears": one_time_arrears,
        "confirmed_invoices": confirmed_invoices,
        "is_gig_worker": is_gig_worker
    }
