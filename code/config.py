import os
from pathlib import Path

# Base Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = REPO_ROOT / 'dataset'
REQUESTS_PATH = DATASET_DIR / 'requests.csv'
SAMPLE_REQUESTS_PATH = DATASET_DIR / 'sample_requests.csv'
PROFILES_PATH = DATASET_DIR / 'financial_profiles.csv'
EVENTS_PATH = DATASET_DIR / 'financial_events.csv'
EXCHANGE_RATES_PATH = DATASET_DIR / 'exchange_rates.csv'
PAYMENT_OPTIONS_PATH = DATASET_DIR / 'request_payment_options.csv'
MESSAGES_PATH = DATASET_DIR / 'messages.csv'
IMAGES_CSV_PATH = DATASET_DIR / 'images.csv'
IMAGES_DIR = DATASET_DIR / 'media' / 'images'

OUTPUT_PATH = REPO_ROOT / 'output.csv'
CACHE_DIR = REPO_ROOT / 'code' / 'cache'
IMAGE_CACHE_PATH = CACHE_DIR / 'images.json'
MESSAGE_CACHE_PATH = CACHE_DIR / 'messages.json'
USAGE_REPORT_PATH = REPO_ROOT / 'evaluation' / 'usage_report.md'

# Financial constants
FORECAST_DAYS = 90
MAX_SPENDING_CHANGES = 3

# Challenge info
DEADLINE_ISO = '2026-09-13T18:00:00+05:30'
SUBMISSION_URL = 'https://www.hackerrank.com/contests/hackerrank-orchestrate-september26/challenges/buy-or-wait/submission'

# Enums
AFFORDABILITY_STATUSES = [
    'affordable_now',
    'affordable_with_plan',
    'affordable_later',
    'not_affordable'
]

PAYMENT_METHODS = [
    'full_payment',
    'partial_payment',
    'installments',
    'wait',
    'not_recommended'
]

def format_amount(val: float) -> str:
    if abs(val - round(val)) < 1e-4:
        return str(int(round(val)))
    return f'{val:.2f}'

