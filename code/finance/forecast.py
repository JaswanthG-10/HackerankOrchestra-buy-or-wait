from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set

from code.models import UserProfile, FinancialEvent, RequestItem

def run_90_day_simulation(
    profile: UserProfile,
    events: List[FinancialEvent],
    resolved_info: dict,
    request_date: str,
    stop_event_ids: Optional[Set[str]] = None,
    reduce_event_map: Optional[Dict[str, float]] = None,
    payment_schedule: Optional[List[Tuple[str, float]]] = None
) -> Tuple[List[Tuple[str, float]], float]:
    stop_event_ids = stop_event_ids or set()
    reduce_event_map = reduce_event_map or {}
    payment_schedule = payment_schedule or []
    
    # Map extra scheduled payments by date
    extra_payments = {}
    for dt, amt in payment_schedule:
        extra_payments[dt] = extra_payments.get(dt, 0.0) + amt

    req_dt = datetime.strptime(request_date, '%Y-%m-%d')
    history = [e for e in events if e.event_date <= request_date and e.status == 'settled']
    
    # Detect salary
    sal_day = 15
    sal_amount = 0.0
    if resolved_info.get('salary_date'):
        sal_day = datetime.strptime(resolved_info['salary_date'], '%Y-%m-%d').day
        
    sal_events = [e for e in history if e.direction == 'credit' and e.category == 'salary']
    if sal_events:
        # Pick the most frequent regular payroll credit day
        regular_sals = [e for e in sal_events if 'bonus' not in e.description.lower() and 'arrears' not in e.description.lower() and 'commission' not in e.description.lower()]
        target_sal = regular_sals[-1] if regular_sals else sal_events[-1]
        sal_amount = target_sal.amount
        if not resolved_info.get('salary_date'):
            from collections import Counter
            days = [datetime.strptime(e.settlement_date, '%Y-%m-%d').day for e in (regular_sals or sal_events)]
            sal_day = Counter(days).most_common(1)[0][0]
            
    if resolved_info.get('salary_update_amt') is not None:
        sal_amount = resolved_info['salary_update_amt']
    if resolved_info.get('salary_ended'):
        sal_amount = 0.0

    # Extract unique recurring debits from history
    debits_hist = [e for e in history if e.direction == 'debit']
    desc_groups = {}
    for e in debits_hist:
        if e.description not in desc_groups:
            desc_groups[e.description] = []
        desc_groups[e.description].append(e)

    recurring_debits = []
    protected_cats = set(profile.expense_categories_to_protect or [])
    for desc, ev_list in desc_groups.items():
        ev_list.sort(key=lambda x: x.event_date)
        last_ev = ev_list[-1]
        if last_ev.category in ['groceries', 'transport', 'dining', 'shopping'] and last_ev.event_type not in ['subscription', 'debt_payment']:
            if last_ev.flexibility not in ['stoppable', 'reducible']:
                continue
        is_fixed_cat = last_ev.category in [
            'rent', 'utilities', 'debt_repayment', 'education', 'insurance',
            'family_support', 'healthcare', 'housing', 'cloud_storage',
            'streaming', 'delivery_membership', 'gym', 'music_subscription'
        ]
        is_fixed_type = last_ev.event_type in ['subscription', 'debt_payment']
        months = set(e.event_date[:7] for e in ev_list)
        is_stoppable = last_ev.flexibility in ['stoppable', 'reducible'] and len(months) >= 2
        
        if is_fixed_cat or is_fixed_type or is_stoppable:
            dt = datetime.strptime(last_ev.event_date, '%Y-%m-%d')
            recurring_debits.append({
                'description': desc,
                'category': last_ev.category,
                'amount': last_ev.amount,
                'day': dt.day,
                'event_id': last_ev.event_id,
                'flexibility': last_ev.flexibility
            })

    # Protected living expenses daily rate (for pre-salary window)
    protected_daily_rate = 0.0
    for cat in (profile.expense_categories_to_protect or []):
        if cat in ['groceries', 'transport', 'dining', 'shopping']:
            cat_evs = [e for e in debits_hist if e.category == cat]
            if cat_evs:
                m_count = len(set(e.event_date[:7] for e in cat_evs))
                total = sum(e.amount for e in cat_evs)
                protected_daily_rate += total / (max(1, m_count) * 30.0)

    # Future scheduled/pending events from dataset
    future_events = [e for e in events if e.settlement_date >= request_date and e.status in ['scheduled', 'pending']]

    curr_bal = profile.current_available_balance
    trajectory = []
    min_headroom = float('inf')
    first_sal_seen = False

    for day_offset in range(90):
        current_dt = req_dt + timedelta(days=day_offset)
        cur_date_str = current_dt.strftime('%Y-%m-%d')
        
        credits_today = 0.0
        debits_today = 0.0

        if not resolved_info.get('salary_ended') and day_offset > 0 and day_offset <= 30:
            debits_today += protected_daily_rate

        # Future events from dataset
        has_scheduled_salary_today = False
        for fe in future_events:
            if fe.settlement_date == cur_date_str:
                if fe.direction == 'credit' and fe.status == 'scheduled':
                    credits_today += fe.amount
                    if fe.category == 'salary':
                        has_scheduled_salary_today = True
                elif fe.direction == 'debit':
                    debits_today += fe.amount

        # Confirmed invoices from messages
        for inv in resolved_info.get('confirmed_invoices', []):
            if inv.get('date') == cur_date_str:
                credits_today += inv.get('amount', 0.0)

        # Salary credit (only if not already credited by a scheduled salary event today)
        if not resolved_info.get('salary_ended') and current_dt.day == sal_day and day_offset > 0:
            first_sal_seen = True
            if not has_scheduled_salary_today:
                credits_today += sal_amount

        # Recurring debits
        for rd in recurring_debits:
            if current_dt.day == rd['day']:
                if day_offset == 0:
                    already_settled = any(
                        e.description == rd['description'] and e.event_date.startswith(cur_date_str[:7])
                        for e in history
                    )
                    if already_settled:
                        continue
                elif current_dt.year == req_dt.year and current_dt.month == req_dt.month:
                    if current_dt.day < req_dt.day:
                        continue
                amt = rd['amount']
                if rd['event_id'] in stop_event_ids:
                    amt = 0.0
                elif rd['event_id'] in reduce_event_map:
                    amt = reduce_event_map[rd['event_id']]
                debits_today += amt

        # Extra request plan payments
        if cur_date_str in extra_payments:
            debits_today += extra_payments[cur_date_str]

        curr_bal += (credits_today - debits_today)
        headroom = curr_bal - profile.minimum_balance_to_keep
        min_headroom = min(min_headroom, headroom)
        trajectory.append((cur_date_str, round(curr_bal, 2)))

    return trajectory, round(min_headroom, 2)
