import sys, os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

from code.loader import (
    load_profiles,
    load_exchange_rates,
    load_image_cache,
    load_financial_events,
    load_payment_options,
    load_requests
)
from code.evidence.message_parser import get_message_facts
from code.models import UserProfile, FinancialEvent, PaymentOption, RequestItem, PlanCandidate, PredictionResult

profiles = load_profiles()
rates = load_exchange_rates()
img_cache = load_image_cache()
events = load_financial_events(profiles, rates, img_cache)
options = load_payment_options()
samples = load_requests(use_samples=True)
df_samples_gt = pd.read_csv('dataset/sample_requests.csv').set_index('request_id')
msg_facts = get_message_facts()

# Group messages by user
user_messages = {}
for m in msg_facts.values():
    u = m['user_id']
    if u not in user_messages:
        user_messages[u] = []
    user_messages[u].append(m)

print('Profiles:', len(profiles), 'Samples:', len(samples))
