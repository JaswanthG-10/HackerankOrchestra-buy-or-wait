import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

from code.models import FinancialEvent

@dataclass
class RecurringObligation:
    description: str
    category: str
    amount: float
    frequency: str # "monthly", "weekly", "biweekly"
    day_of_month: Optional[int] = None
    day_of_week: Optional[int] = None # 0=Monday, 6=Sunday
    last_date: Optional[str] = None
    flexibility: str = "fixed" # "fixed", "reducible", "stoppable", "reducible_or_stoppable"
    minimum_allowed_amount: Optional[float] = None
    event_id: Optional[str] = None

def normalize_description(desc: str) -> str:
    s = str(desc).lower().strip()
    s = re.sub(r'#?\b[0-9a-fA-F\-]{4,}\b', '', s)
    s = re.sub(r'\b\d+\b', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def detect_recurring_obligations(
    events: List[FinancialEvent],
    request_date: str
) -> List[RecurringObligation]:
    """
    Infers recurring debit obligations from historical settled events before request_date.
    Uses normalized identity grouping and interval consistency.
    Filters out inactive recurrences older than 60 days.
    """
    req_dt = datetime.strptime(request_date, "%Y-%m-%d")
    history = [
        e for e in events 
        if e.event_date <= request_date and e.status == "settled" and e.direction == "debit"
    ]
    
    # Group by normalized identity
    norm_groups: Dict[Tuple[str, str], List[FinancialEvent]] = {}
    for e in history:
        key = (normalize_description(e.description), e.category)
        norm_groups.setdefault(key, []).append(e)
        
    recurring: List[RecurringObligation] = []
    
    for (norm_desc, cat), evs in norm_groups.items():
        if len(evs) < 2:
            continue
            
        evs.sort(key=lambda x: x.event_date)
        last_ev = evs[-1]
        
        # Recency check: must have occurred within last 65 days
        days_since_last = (req_dt - datetime.strptime(last_ev.event_date, "%Y-%m-%d")).days
        if days_since_last > 65:
            continue
            
        dates = [datetime.strptime(e.event_date, "%Y-%m-%d") for e in evs]
        deltas = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        
        if not deltas:
            continue
            
        med_delta = float(np.median(deltas))
        
        # Use last settled amount as current recurring rate or median of recent 3
        recent_evs = evs[-3:] if len(evs) >= 3 else evs
        recent_amts = [e.amount for e in recent_evs]
        amount = float(np.median(recent_amts))
        
        frequency = None
        dom = None
        dow = None
        
        if 6.0 <= med_delta <= 8.5:
            frequency = "weekly"
            dow = dates[-1].weekday()
        elif 13.0 <= med_delta <= 16.5:
            frequency = "biweekly"
            dow = dates[-1].weekday()
        elif 26.0 <= med_delta <= 33.0:
            frequency = "monthly"
            days = [d.day for d in dates]
            dom = Counter(days).most_common(1)[0][0]
        else:
            days = [d.day for d in dates]
            most_common_day, count = Counter(days).most_common(1)[0]
            if count >= 2 and len(evs) >= 2 and (dates[-1] - dates[0]).days >= 45:
                frequency = "monthly"
                dom = most_common_day
                
        if frequency:
            recurring.append(RecurringObligation(
                description=last_ev.description,
                category=last_ev.category,
                amount=amount,
                frequency=frequency,
                day_of_month=dom,
                day_of_week=dow,
                last_date=last_ev.event_date,
                flexibility=last_ev.flexibility,
                minimum_allowed_amount=last_ev.minimum_allowed_amount,
                event_id=last_ev.event_id
            ))

    # Category-level fallback for ungrouped recurring debits (e.g. rotating merchants under one category)
    existing_cats = set(r.category for r in recurring)
    cat_groups: Dict[str, List[FinancialEvent]] = {}
    for e in history:
        cat_groups.setdefault(e.category, []).append(e)

    for cat, evs in cat_groups.items():
        if cat in existing_cats or len(evs) < 2:
            continue
        evs.sort(key=lambda x: x.event_date)
        last_ev = evs[-1]
        days_since_last = (req_dt - datetime.strptime(last_ev.event_date, "%Y-%m-%d")).days
        if days_since_last > 65:
            continue
        dates = [datetime.strptime(e.event_date, "%Y-%m-%d") for e in evs]
        deltas = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        if not deltas:
            continue
        med_delta = float(np.median(deltas))
        recent_evs = evs[-3:] if len(evs) >= 3 else evs
        recent_amts = [e.amount for e in recent_evs]
        amount = float(np.median(recent_amts))

        frequency = None
        dom = None
        dow = None
        if 6.0 <= med_delta <= 8.5:
            frequency = "weekly"
            dow = dates[-1].weekday()
        elif 13.0 <= med_delta <= 16.5:
            frequency = "biweekly"
            dow = dates[-1].weekday()
        elif 19.5 <= med_delta <= 22.5:
            frequency = "every_21_days"
        elif 26.0 <= med_delta <= 33.0:
            frequency = "monthly"
            days = [d.day for d in dates]
            dom = Counter(days).most_common(1)[0][0]

        if frequency:
            recurring.append(RecurringObligation(
                description=last_ev.description,
                category=last_ev.category,
                amount=amount,
                frequency=frequency,
                day_of_month=dom,
                day_of_week=dow,
                last_date=last_ev.event_date,
                flexibility=last_ev.flexibility,
                minimum_allowed_amount=last_ev.minimum_allowed_amount,
                event_id=last_ev.event_id
            ))

    return recurring
