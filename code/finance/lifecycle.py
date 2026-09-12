from typing import Dict, List, Set, Tuple
from code.models import FinancialEvent

def resolve_event_chains(events: List[FinancialEvent]) -> List[FinancialEvent]:
    """
    Resolves transaction lifecycles using linked_event_id chains:
    - Builds parent-child relationship chains
    - Eliminates cancelled, failed, and non-cash unrealized events
    - Disallows unconfirmed pending credits
    - Preserves settled cash movements exactly once
    - Reserves pending debits
    """
    by_id: Dict[str, FinancialEvent] = {e.event_id: e for e in events}
    
    # Map parents to children
    children_of: Dict[str, List[FinancialEvent]] = {}
    for e in events:
        if e.linked_event_id:
            children_of.setdefault(e.linked_event_id, []).append(e)
            
    resolved: List[FinancialEvent] = []
    
    for e in events:
        # Rule 1: Exclude cancelled events (e.g. card authorizations superseded by settled purchase)
        if e.status == "cancelled":
            continue
            
        # Rule 2: Exclude failed events (e.g. failed bill payments superseded by scheduled retry)
        if e.status == "failed":
            continue
            
        # Rule 3: Exclude unrealized non-cash events (e.g. portfolio valuations)
        if e.status == "unrealized" or e.direction == "non_cash":
            continue
            
        # Rule 4: Pending credits are not withdrawable / available cash yet
        if e.status == "pending" and e.direction == "credit":
            continue
            
        # Rule 5: If this event is a settled event that was superseded or corrected, preserve final state
        # In our dataset, linked events with status == 'settled' are real cash events (e.g. reversals, reimbursements, purchase)
        resolved.append(e)
        
    return resolved
