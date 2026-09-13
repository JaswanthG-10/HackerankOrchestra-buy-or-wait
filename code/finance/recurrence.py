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

def detect_recurring_obligations(
    events: List[FinancialEvent],
    request_date: str
) -> List[RecurringObligation]:
    """
    Infers recurring debit obligations from historical settled events before request_date.
    Uses interval consistency:
    - 6 to 8 days: weekly
    - 13 to 16 days: bi-weekly
    - 27 to 33 days: monthly
    """
    req_dt = datetime.strptime(request_date, "%Y-%m-%d")
    history = [
        e for e in events 
        if e.event_date <= request_date and e.status == "settled" and e.direction == "debit"
    ]
    
    # Group by description
    desc_groups: Dict[str, List[FinancialEvent]] = {}
    for e in history:
        desc_groups.setdefault(e.description, []).append(e)
        
    recurring: List[RecurringObligation] = []
    
    for desc, evs in desc_groups.items():
        if len(evs) < 2:
            continue
            
        evs.sort(key=lambda x: x.event_date)
        dates = [datetime.strptime(e.event_date, "%Y-%m-%d") for e in evs]
        deltas = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        
        if not deltas:
            continue
            
        med_delta = float(np.median(deltas))
        last_ev = evs[-1]
        
        # Use last settled amount as the current recurring rate
        # If amount varied widely (e.g. utilities), median of recent 3
        recent_evs = evs[-3:] if len(evs) >= 3 else evs
        recent_amts = [e.amount for e in recent_evs]
        amount = float(np.median(recent_amts))
        
        # Determine frequency
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
            # Check if all events share the same day of month (+/- 1 day)
            days = [d.day for d in dates]
            most_common_day, count = Counter(days).most_common(1)[0]
            if count >= 2 and len(evs) >= 2 and (dates[-1] - dates[0]).days >= 45:
                frequency = "monthly"
                dom = most_common_day
                
        if frequency:
            recurring.append(RecurringObligation(
                description=desc,
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
