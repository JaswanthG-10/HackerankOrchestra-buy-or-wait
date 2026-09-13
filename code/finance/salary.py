from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import Counter
from code.models import FinancialEvent, UserProfile

@dataclass
class SalaryRule:
    amount: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    recurring: bool = True
    one_time: bool = False
    next_cycle_only: bool = False
    pay_day: int = 15
    rule_type: str = "base" # "base", "increase", "reduction", "first_salary", "arrears", "invoice"

def resolve_salary_plan(
    profile: UserProfile,
    events: List[FinancialEvent],
    user_messages: List[dict],
    request_date: str
) -> Dict[str, any]:
    """
    Builds the forward salary schedule and salary rules:
    - Incorporates explicit scheduled future salary from events
    - Determines baseline recurring salary and pay day
    - Handles contract endings, temporary leaves, date changes, arrears, confirmed invoices
    - Never terminates salary on pending payout; requires explicit termination evidence
    """
    req_dt = datetime.strptime(request_date, "%Y-%m-%d")
    history = [e for e in events if e.event_date <= request_date and e.status == "settled"]
    
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
    salary_rules: List[SalaryRule] = []
    
    # Check if latest settled salary in history indicates final payroll
    settled_sals = [e for e in history if e.direction == "credit" and e.category == "salary"]
    if settled_sals and "final employer payroll" in settled_sals[-1].description.lower():
        salary_ended = True
        
    for msg in user_messages:
        fact_type = msg.get("fact_type")
        txt = str(msg.get("summary", "")).lower()
        
        # Only explicit termination evidence terminates salary
        if fact_type == "contract_ended" or any(w in txt for w in ["contract ended", "employment ended", "no further payroll", "seasonal work ended"]):
            salary_ended = True
        elif fact_type == "salary_update":
            amt = msg.get("amount")
            eff_dt = msg.get("effective_date")
            if "unpaid leave" in txt or "next salary is reduced" in txt or "next payroll" in txt:
                next_sal_amount = float(amt) if amt is not None else None
                if amt is not None:
                    salary_rules.append(SalaryRule(amount=float(amt), start_date=eff_dt, recurring=False, next_cycle_only=True, rule_type="reduction"))
            else:
                if amt is not None:
                    perm_sal_amount = float(amt)
                if eff_dt:
                    next_sal_date = eff_dt
                    perm_sal_day = datetime.strptime(next_sal_date, "%Y-%m-%d").day
                if amt is not None:
                    salary_rules.append(SalaryRule(amount=float(amt), start_date=eff_dt, recurring=True, pay_day=perm_sal_day, rule_type="increase"))
        elif fact_type == "salary_date_change":
            if msg.get("effective_date"):
                next_sal_date = msg["effective_date"]
                perm_sal_day = datetime.strptime(next_sal_date, "%Y-%m-%d").day
        elif fact_type == "confirmed_income":
            if msg.get("amount") and msg.get("effective_date"):
                inv_amt = float(msg["amount"])
                inv_dt = msg["effective_date"]
                confirmed_invoices.append({
                    "amount": inv_amt,
                    "date": inv_dt
                })
                salary_rules.append(SalaryRule(amount=inv_amt, start_date=inv_dt, recurring=False, one_time=True, rule_type="invoice"))
        elif "first salary" in txt:
            if msg.get("amount"):
                perm_sal_amount = float(msg["amount"])
            if msg.get("effective_date"):
                first_sal_date = msg["effective_date"]
                perm_sal_day = datetime.strptime(first_sal_date, "%Y-%m-%d").day
            if msg.get("amount") and msg.get("effective_date"):
                salary_rules.append(SalaryRule(amount=float(msg["amount"]), start_date=first_sal_date, recurring=True, pay_day=perm_sal_day, rule_type="first_salary"))
        elif "arrears" in txt and msg.get("amount"):
            one_time_arrears = float(msg["amount"])
            eff_dt = msg.get("effective_date") or f"{request_date[:7]}-{perm_sal_day:02d}"
            salary_rules.append(SalaryRule(amount=one_time_arrears, start_date=eff_dt, recurring=False, one_time=True, rule_type="arrears"))

    is_gig_worker = any(
        any(w in e.description.lower() for w in ["gig", "platform payout", "app earnings", "task marketplace", "driver platform", "delivery platform"])
        for e in settled_sals
    )

    if perm_sal_amount > 0 and not salary_rules and not is_gig_worker:
        salary_rules.append(SalaryRule(amount=perm_sal_amount, recurring=True, pay_day=perm_sal_day, rule_type="base"))

    return {
        "salary_ended": salary_ended,
        "is_gig_worker": is_gig_worker,
        "base_sal_amount": base_sal_amount,
        "perm_sal_amount": perm_sal_amount,
        "perm_sal_day": perm_sal_day,
        "next_sal_amount": next_sal_amount,
        "next_sal_date": next_sal_date,
        "first_sal_date": first_sal_date,
        "one_time_arrears": one_time_arrears,
        "confirmed_invoices": confirmed_invoices,
        "rules": salary_rules
    }
