from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
from code.models import FinancialEvent

def resolve_event_chains(events: List[FinancialEvent]) -> List[FinancialEvent]:
    """
    True linked-event lifecycle resolution using graph/chain traversal.
    
    Traverses linked_event_id relationships across events, identifies roots and chains,
    and collapses state-transition chains into effective financial cash events.
    
    Priority & Handling Rules:
    - Failed, cancelled, and non-cash unrealized events are excluded.
    - Pending credits are excluded (not withdrawable cash yet).
    - Pending debits are preserved (to reserve funds).
    - Scheduled debits/credits are preserved unless superseded by pending/settled/cancelled states.
    - State transition chains (e.g. scheduled -> pending -> settled, or failed -> scheduled retry,
      or card authorization -> settled purchase): collapsed to the effective final state.
    - Distinct real cash legs in a relationship (e.g., settled debit + settled reversal credit):
      each distinct settled leg is preserved.
    """
    by_id: Dict[str, FinancialEvent] = {e.event_id: e for e in events}
    
    # Build bidirectional graph of linked events
    adj: Dict[str, Set[str]] = defaultdict(set)
    for e in events:
        if e.linked_event_id and e.linked_event_id in by_id:
            adj[e.event_id].add(e.linked_event_id)
            adj[e.linked_event_id].add(e.event_id)
            
    visited: Set[str] = set()
    components: List[List[FinancialEvent]] = []
    
    for e in events:
        if e.event_id in visited:
            continue
        # BFS component discovery
        comp_ids: List[str] = []
        queue = deque([e.event_id])
        visited.add(e.event_id)
        while queue:
            curr = queue.popleft()
            comp_ids.append(curr)
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        components.append([by_id[cid] for cid in comp_ids])
        
    resolved: List[FinancialEvent] = []
    
    for comp in components:
        if len(comp) == 1:
            ev = comp[0]
            # Single unlinked event filtering
            if ev.status in ("cancelled", "failed", "unrealized"):
                continue
            if ev.direction == "non_cash":
                continue
            if ev.status == "pending" and ev.direction == "credit":
                continue
            resolved.append(ev)
            continue
            
        # Multi-event connected chain
        # Sort chronologically by event_date, then settlement_date, then event_id
        sorted_comp = sorted(
            comp,
            key=lambda x: (
                x.event_date or "",
                x.settlement_date or x.event_date or "",
                x.event_id
            )
        )
        
        # Check for state-transition progression where a later event supersedes an earlier one
        superseded_ids: Set[str] = set()
        
        for i, ev_pre in enumerate(sorted_comp):
            if ev_pre.status in ("cancelled", "failed", "unrealized") or ev_pre.direction == "non_cash":
                superseded_ids.add(ev_pre.event_id)
                continue
            if ev_pre.status == "pending" and ev_pre.direction == "credit":
                superseded_ids.add(ev_pre.event_id)
                continue
                
            # Check if this event was superseded by a later event in the same chain
            for j in range(i + 1, len(sorted_comp)):
                ev_post = sorted_comp[j]
                is_related = (
                    ev_post.linked_event_id == ev_pre.event_id
                    or ev_pre.linked_event_id == ev_post.event_id
                    or (ev_pre.category == ev_post.category and ev_pre.direction == ev_post.direction)
                )
                if not is_related:
                    continue
                    
                # If post event is cancelled/reversed, and pre event was scheduled/pending:
                if ev_post.status == "cancelled" and ev_pre.status in ("scheduled", "pending"):
                    superseded_ids.add(ev_pre.event_id)
                # If post event is settled with same direction:
                elif ev_post.status == "settled" and ev_pre.direction == ev_post.direction:
                    if ev_pre.status in ("scheduled", "pending"):
                        superseded_ids.add(ev_pre.event_id)
                # If post event is scheduled retry, supersede failed attempt:
                elif ev_post.status == "scheduled" and ev_pre.status == "failed":
                    superseded_ids.add(ev_pre.event_id)
                    
        for ev in sorted_comp:
            if ev.event_id in superseded_ids:
                continue
            if ev.status in ("cancelled", "failed", "unrealized") or ev.direction == "non_cash":
                continue
            if ev.status == "pending" and ev.direction == "credit":
                continue
            resolved.append(ev)
            
    return resolved
