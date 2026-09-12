from datetime import datetime
from typing import Optional, List
from code.models import UserProfile, RequestItem, PlanCandidate, FinancialEvent

def format_currency_amount(amount: float, currency: str) -> str:
    if currency == 'IDR':
        # IDR usually integer
        if amount == int(amount):
            return f'{currency} {int(amount):,}'
        return f'{currency} {amount:,.2f}'
    elif currency == 'INR':
        if amount == int(amount):
            return f'{currency} {int(amount):,}'
        return f'{currency} {amount:,.2f}'
    else:
        if amount == int(amount):
            return f'{currency} {int(amount):,}'
        return f'{currency} {amount:,.2f}'

def format_date_friendly(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        # e.g., '8 August 2025' or '15 November 2019'
        day = dt.day
        month_name = dt.strftime('%B')
        year = dt.year
        return f'{day} {month_name} {year}'
    except Exception:
        return date_str

def generate_decision_explanation(
    profile: UserProfile,
    request: RequestItem,
    candidate: Optional[PlanCandidate],
    amount_safe_to_pay: float,
    earliest_date_for_full_payment: Optional[str],
    all_events: List[FinancialEvent]
) -> str:
    curr = profile.home_currency
    min_bal_str = format_currency_amount(profile.minimum_balance_to_keep, curr)

    if not candidate or candidate.method == 'not_recommended':
        dl_friendly = format_date_friendly(request.desired_completion_date)
        if amount_safe_to_pay > 0:
            safe_str = format_currency_amount(amount_safe_to_pay, curr)
            req_str = format_currency_amount(request.requested_amount, curr)
            return f'Do not proceed with the {req_str} request. Although {safe_str} is available today, the full amount cannot be completed safely within 90 days.'
        return f'Do not make this payment by {dl_friendly}. None of the available options keeps the {min_bal_str} minimum protected.'

    method = candidate.method

    if method == 'full_payment':
        req_str = format_currency_amount(request.requested_amount, curr)
        if candidate.spending_changes:
            # Describe changes
            change_descriptions = []
            ev_map = {e.event_id: e for e in all_events}
            for sc in candidate.spending_changes:
                if sc.startswith('stop:'):
                    ev_id = sc.split(':')[1]
                    ev = ev_map.get(ev_id)
                    desc = ev.description.lower() if ev else 'subscription'
                    change_descriptions.append(f'Stop the {desc}')
                elif sc.startswith('reduce_to:'):
                    parts = sc.split(':')
                    ev_id = parts[1]
                    new_amt = float(parts[2])
                    ev = ev_map.get(ev_id)
                    desc = ev.description.lower() if ev else 'expense'
                    amt_str = format_currency_amount(new_amt, curr)
                    change_descriptions.append(f'reduce the {desc} to {amt_str}')
            
            changes_str = ' and '.join(change_descriptions)
            return f'{changes_str}, then pay {req_str} today. This leaves at least {min_bal_str} available.'
        else:
            return f'Pay {req_str} today. This leaves at least {min_bal_str} available over the next 90 days.'

    elif method == 'installments':
        n = candidate.num_payments
        start_friendly = format_date_friendly(candidate.start_date)
        per_pay = candidate.schedule[0][1] if candidate.schedule else 0.0
        pay_str = format_currency_amount(per_pay, curr)
        return f'Use {n} installments of {pay_str}, starting {start_friendly}. This leaves at least {min_bal_str} available.'

    elif method == 'wait':
        req_str = format_currency_amount(request.requested_amount, curr)
        earliest_friendly = format_date_friendly(earliest_date_for_full_payment or candidate.start_date)
        return f'Pay {req_str} in full on {earliest_friendly}. Paying earlier would take the balance below the {min_bal_str} minimum.'

    elif method == 'partial_payment':
        p1 = candidate.schedule[0][1]
        p2 = candidate.schedule[1][1]
        p1_str = format_currency_amount(p1, curr)
        p2_str = format_currency_amount(p2, curr)
        p2_date_friendly = format_date_friendly(candidate.schedule[1][0])
        return f'Pay {p1_str} today and the remaining {p2_str} on {p2_date_friendly}. This completes the full request and keeps the {min_bal_str} minimum protected.'

    return f'Recommendation determined per financial safety check.'
