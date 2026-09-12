import copy
from typing import Dict, List, Optional
from code.models import FinancialEvent, UserProfile
from code.finance.lifecycle import resolve_event_chains
from code.finance.salary import resolve_salary_plan

def resolve_user_events(
    user_id: str,
    raw_events: List[FinancialEvent],
    profile: UserProfile,
    user_messages: List[dict],
    request_date: str
) -> Dict[str, any]:
    clean_events = resolve_event_chains(raw_events)
    salary_info = resolve_salary_plan(profile, clean_events, user_messages, request_date)

    return {
        'events': clean_events,
        'messages': user_messages,
        'salary_info': salary_info,
        'salary_update_amt': salary_info.get('next_sal_amount') or salary_info.get('perm_sal_amount'),
        'salary_date': salary_info.get('next_sal_date') or f"{request_date[:7]}-{salary_info.get('perm_sal_day', 15):02d}",
        'salary_ended': salary_info.get('salary_ended', False),
        'confirmed_invoices': salary_info.get('confirmed_invoices', [])
    }

