import json
import os
import pandas as pd
from typing import Dict, List, Optional, Tuple

from code.config import (
    PROFILES_PATH,
    EVENTS_PATH,
    EXCHANGE_RATES_PATH,
    PAYMENT_OPTIONS_PATH,
    REQUESTS_PATH,
    SAMPLE_REQUESTS_PATH,
    IMAGE_CACHE_PATH,
    MESSAGE_CACHE_PATH,
    IMAGES_CSV_PATH
)
from code.models import (
    UserProfile,
    FinancialEvent,
    PaymentOption,
    RequestItem
)

def parse_pipe_list(val) -> List[str]:
    if pd.isna(val) or not val:
        return []
    return [s.strip() for s in str(val).split('|') if s.strip()]

def load_profiles() -> Dict[str, UserProfile]:
    df = pd.read_csv(PROFILES_PATH)
    profiles = {}
    for _, r in df.iterrows():
        u_id = str(r['user_id'])
        max_inst = float(r['max_installment_months']) if pd.notnull(r['max_installment_months']) else None
        profiles[u_id] = UserProfile(
            user_id=u_id,
            home_currency=str(r['home_currency']),
            current_available_balance=float(r['current_available_balance']),
            minimum_balance_to_keep=float(r['minimum_balance_to_keep']),
            financial_priorities=parse_pipe_list(r.get('financial_priorities')),
            expense_categories_to_protect=parse_pipe_list(r.get('expense_categories_to_protect')),
            expense_categories_user_is_willing_to_reduce=parse_pipe_list(r.get('expense_categories_user_is_willing_to_reduce')),
            expense_categories_user_is_willing_to_stop=parse_pipe_list(r.get('expense_categories_user_is_willing_to_stop')),
            payment_methods_user_will_consider=parse_pipe_list(r.get('payment_methods_user_will_consider')),
            max_installment_months=max_inst
        )
    return profiles

def load_exchange_rates() -> Dict[Tuple[str, str, str], float]:
    df = pd.read_csv(EXCHANGE_RATES_PATH)
    rates = {}
    for _, r in df.iterrows():
        key = (str(r['rate_date']), str(r['from_currency']), str(r['to_currency']))
        rates[key] = float(r['rate'])
    return rates

def load_image_cache() -> Dict[str, dict]:
    # Maps event_id -> dict with amount, currency, etc.
    event_image_map = {}
    if os.path.exists(IMAGE_CACHE_PATH):
        try:
            with open(IMAGE_CACHE_PATH, 'r', encoding='utf-8') as f:
                img_data = json.load(f)
            for img_id, item in img_data.items():
                ev_id = item.get('related_event_id')
                if ev_id:
                    event_image_map[str(ev_id)] = item
        except Exception:
            pass
    return event_image_map

def load_message_cache() -> Dict[str, list]:
    # Maps user_id -> list of message fact dicts
    user_msg_map = {}
    if os.path.exists(MESSAGE_CACHE_PATH):
        try:
            with open(MESSAGE_CACHE_PATH, 'r', encoding='utf-8') as f:
                msg_data = json.load(f)
            for m_id, item in msg_data.items():
                u_id = str(item.get('user_id'))
                if u_id not in user_msg_map:
                    user_msg_map[u_id] = []
                user_msg_map[u_id].append(item)
        except Exception:
            pass
    return user_msg_map

def load_financial_events(
    profiles: Dict[str, UserProfile],
    rates: Dict[Tuple[str, str, str], float],
    image_cache: Dict[str, dict]
) -> Dict[str, List[FinancialEvent]]:
    df = pd.read_csv(EVENTS_PATH)
    user_events = {}

    for _, r in df.iterrows():
        u_id = str(r['user_id'])
        ev_id = str(r['event_id'])
        home_currency = profiles[u_id].home_currency
        ev_currency = str(r['currency'])
        settle_date = str(r['settlement_date'])
        ev_date = str(r['event_date'])

        # Resolve blank amount from image cache if needed
        raw_amt = r['amount']
        if pd.isna(raw_amt):
            if ev_id in image_cache:
                raw_amt = float(image_cache[ev_id]['amount'])
            else:
                raw_amt = 0.0
        else:
            raw_amt = float(raw_amt)

        # Convert to home currency if foreign currency
        amt = raw_amt
        if ev_currency != home_currency:
            rate_key = (settle_date, ev_currency, home_currency)
            if rate_key in rates:
                amt = raw_amt * rates[rate_key]

        # Minimum allowed amount for reducible items
        min_amt = None
        if pd.notnull(r['minimum_allowed_amount']):
            min_raw = float(r['minimum_allowed_amount'])
            min_amt = min_raw
            if ev_currency != home_currency:
                rate_key = (settle_date, ev_currency, home_currency)
                if rate_key in rates:
                    min_amt = min_raw * rates[rate_key]

        linked_id = str(r['linked_event_id']) if pd.notnull(r['linked_event_id']) else None

        event = FinancialEvent(
            event_id=ev_id,
            user_id=u_id,
            event_type=str(r['event_type']),
            description=str(r['description']),
            category=str(r['category']),
            direction=str(r['direction']),
            amount=round(amt, 2),
            raw_amount=raw_amt,
            currency=home_currency,
            event_date=ev_date,
            settlement_date=settle_date,
            status=str(r['status']),
            linked_event_id=linked_id,
            flexibility=str(r['flexibility']) if pd.notnull(r['flexibility']) else 'fixed',
            minimum_allowed_amount=round(min_amt, 2) if min_amt is not None else None
        )

        if u_id not in user_events:
            user_events[u_id] = []
        user_events[u_id].append(event)

    for u_id in user_events:
        user_events[u_id].sort(key=lambda x: x.event_date)

    return user_events

def load_payment_options() -> Dict[str, List[PaymentOption]]:
    df = pd.read_csv(PAYMENT_OPTIONS_PATH)
    options = {}
    for _, r in df.iterrows():
        req_id = str(r['request_id'])
        opt = PaymentOption(
            payment_option_id=str(r['payment_option_id']),
            request_id=req_id,
            payment_method=str(r['payment_method']),
            payment_amount=float(r['payment_amount']),
            number_of_payments=int(r['number_of_payments']),
            first_payment_date=str(r['first_payment_date']),
            payment_frequency_days=float(r['payment_frequency_days']) if pd.notnull(r['payment_frequency_days']) else None,
            financing_fee=float(r['financing_fee']) if pd.notnull(r['financing_fee']) else 0.0,
            total_payable_amount=float(r['total_payable_amount']) if pd.notnull(r['total_payable_amount']) else 0.0
        )
        if req_id not in options:
            options[req_id] = []
        options[req_id].append(opt)
    return options

def load_requests(use_samples: bool = False) -> List[RequestItem]:
    path = SAMPLE_REQUESTS_PATH if use_samples else REQUESTS_PATH
    df = pd.read_csv(path)
    requests = []
    for _, r in df.iterrows():
        req = RequestItem(
            request_id=str(r['request_id']),
            user_id=str(r['user_id']),
            request_date=str(r['request_date']),
            request_type=str(r['request_type']),
            requested_amount=float(r['requested_amount']),
            desired_completion_date=str(r['desired_completion_date']),
            allows_partial_payment=str(r['allows_partial_payment']).strip().lower() in ['true', '1', 'yes'],
            request_text=str(r['request_text'])
        )
        requests.append(req)
    return requests
