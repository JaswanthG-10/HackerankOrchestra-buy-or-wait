import copy
from typing import Dict, List, Optional
from code.models import FinancialEvent, UserProfile

def resolve_user_events(
    user_id: str,
    raw_events: List[FinancialEvent],
    profile: UserProfile,
    user_messages: List[dict],
    request_date: str
) -> Dict[str, any]:
    events = [copy.deepcopy(e) for e in raw_events]

    # Check messages for user
    salary_update_amt = None
    salary_date = None
    salary_ended = False
    rent_increase_pct = None
    confirmed_invoices = []

    # Check if latest settled salary in history indicates final payroll
    settled_salaries = [e for e in events if e.category == 'salary' and e.status == 'settled' and e.event_date <= request_date]
    if settled_salaries:
        settled_salaries.sort(key=lambda x: x.event_date)
        if 'final employer payroll' in settled_salaries[-1].description.lower():
            salary_ended = True

    for msg in user_messages:
        fact_type = msg.get('fact_type')
        if fact_type == 'salary_update':
            if msg.get('amount') is not None:
                salary_update_amt = float(msg['amount'])
            if msg.get('effective_date'):
                salary_date = msg['effective_date']
        elif fact_type == 'salary_date_change':
            if msg.get('effective_date'):
                salary_date = msg['effective_date']
        elif fact_type == 'contract_ended':
            salary_ended = True
        elif fact_type == 'rent_increase':
            if msg.get('percentage_change') is not None:
                rent_increase_pct = float(msg['percentage_change'])
        elif fact_type == 'confirmed_income':
            if msg.get('amount') is not None and msg.get('effective_date'):
                confirmed_invoices.append({
                    'amount': float(msg['amount']),
                    'date': msg['effective_date'],
                    'description': msg.get('summary', 'Confirmed invoice payout')
                })

    # Filter out cancelled, failed, unrealized
    valid_events = []
    for e in events:
        if e.status in ['cancelled', 'failed', 'unrealized']:
            continue
        # Exclude pending credits
        if e.status == 'pending' and e.direction == 'credit':
            continue
        
        # Apply rent increase if applicable
        if rent_increase_pct and e.category == 'rent':
            e.amount = round(e.amount * (1.0 + rent_increase_pct / 100.0), 2)
            
        valid_events.append(e)

    return {
        'events': valid_events,
        'salary_update_amt': salary_update_amt,
        'salary_date': salary_date,
        'salary_ended': salary_ended,
        'confirmed_invoices': confirmed_invoices
    }
