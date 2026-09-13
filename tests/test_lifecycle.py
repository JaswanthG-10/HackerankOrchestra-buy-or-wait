import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from code.models import FinancialEvent
from code.finance.lifecycle import resolve_event_chains

def make_event(event_id, status, direction, amount=100.0, linked_id=None, date='2024-01-01', cat='test'):
    return FinancialEvent(
        event_id=event_id,
        user_id='u1',
        event_type='transaction',
        description=f'Event {event_id}',
        category=cat,
        direction=direction,
        amount=amount,
        raw_amount=amount,
        currency='USD',
        event_date=date,
        settlement_date=date,
        status=status,
        linked_event_id=linked_id,
        flexibility='fixed',
        minimum_allowed_amount=None
    )

def test_scheduled_pending_settled():
    # scheduled -> pending -> settled collapses to settled
    e1 = make_event('e1', 'scheduled', 'debit', 100.0, date='2024-01-01')
    e2 = make_event('e2', 'pending', 'debit', 100.0, linked_id='e1', date='2024-01-02')
    e3 = make_event('e3', 'settled', 'debit', 100.0, linked_id='e2', date='2024-01-03')
    res = resolve_event_chains([e1, e2, e3])
    assert len(res) == 1
    assert res[0].event_id == 'e3'
    assert res[0].status == 'settled'
    print('PASS: test_scheduled_pending_settled')

def test_scheduled_cancelled():
    # scheduled -> cancelled results in 0 events
    e1 = make_event('e1', 'scheduled', 'debit', 100.0, date='2024-01-01')
    e2 = make_event('e2', 'cancelled', 'debit', 100.0, linked_id='e1', date='2024-01-02')
    res = resolve_event_chains([e1, e2])
    assert len(res) == 0
    print('PASS: test_scheduled_cancelled')

def test_failed_retry_settled():
    # failed -> scheduled retry -> settled retry collapses to settled retry
    e1 = make_event('e1', 'failed', 'debit', 50.0, date='2024-01-01')
    e2 = make_event('e2', 'scheduled', 'debit', 50.0, linked_id='e1', date='2024-01-02')
    e3 = make_event('e3', 'settled', 'debit', 50.0, linked_id='e2', date='2024-01-03')
    res = resolve_event_chains([e1, e2, e3])
    assert len(res) == 1
    assert res[0].event_id == 'e3'
    print('PASS: test_failed_retry_settled')

def test_pending_credit_to_settled_credit():
    # pending credit -> settled credit collapses to settled credit
    e1 = make_event('e1', 'pending', 'credit', 200.0, date='2024-01-01')
    e2 = make_event('e2', 'settled', 'credit', 200.0, linked_id='e1', date='2024-01-02')
    res = resolve_event_chains([e1, e2])
    assert len(res) == 1
    assert res[0].event_id == 'e2'
    print('PASS: test_pending_credit_to_settled_credit')

def test_authorization_to_settled_purchase():
    # Card authorization (cancelled/pending) -> settled card purchase
    e1 = make_event('e1', 'cancelled', 'debit', 80.0, date='2024-01-01')
    e2 = make_event('e2', 'settled', 'debit', 80.0, linked_id='e1', date='2024-01-02')
    res = resolve_event_chains([e1, e2])
    assert len(res) == 1
    assert res[0].event_id == 'e2'
    print('PASS: test_authorization_to_settled_purchase')

def test_refund_pending_to_refund_settled():
    # Original purchase (settled debit) -> pending refund (pending credit) -> settled refund (settled credit)
    e1 = make_event('e1', 'settled', 'debit', 50.0, date='2024-01-01')
    e2 = make_event('e2', 'pending', 'credit', 50.0, linked_id='e1', date='2024-01-02')
    e3 = make_event('e3', 'settled', 'credit', 50.0, linked_id='e2', date='2024-01-03')
    res = resolve_event_chains([e1, e2, e3])
    assert len(res) == 2
    assert set(e.event_id for e in res) == {'e1', 'e3'}
    print('PASS: test_refund_pending_to_refund_settled')

if __name__ == '__main__':
    test_scheduled_pending_settled()
    test_scheduled_cancelled()
    test_failed_retry_settled()
    test_pending_credit_to_settled_credit()
    test_authorization_to_settled_purchase()
    test_refund_pending_to_refund_settled()
    print('ALL LIFECYCLE UNIT TESTS PASSED!')
