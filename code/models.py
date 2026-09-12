from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class UserProfile:
    user_id: str
    home_currency: str
    current_available_balance: float
    minimum_balance_to_keep: float
    financial_priorities: List[str] = field(default_factory=list)
    expense_categories_to_protect: List[str] = field(default_factory=list)
    expense_categories_user_is_willing_to_reduce: List[str] = field(default_factory=list)
    expense_categories_user_is_willing_to_stop: List[str] = field(default_factory=list)
    payment_methods_user_will_consider: List[str] = field(default_factory=list)
    max_installment_months: Optional[float] = None

@dataclass
class FinancialEvent:
    event_id: str
    user_id: str
    event_type: str
    description: str
    category: str
    direction: str # 'credit' | 'debit'
    amount: float # in home_currency
    raw_amount: float
    currency: str
    event_date: str # YYYY-MM-DD
    settlement_date: str # YYYY-MM-DD
    status: str # settled | pending | scheduled | cancelled | failed | unrealized
    linked_event_id: Optional[str] = None
    flexibility: str = 'fixed' # fixed | reducible | stoppable | reducible_or_stoppable
    minimum_allowed_amount: Optional[float] = None

@dataclass
class PaymentOption:
    payment_option_id: str
    request_id: str
    payment_method: str
    payment_amount: float
    number_of_payments: int
    first_payment_date: str
    payment_frequency_days: Optional[float] = None
    financing_fee: float = 0.0
    total_payable_amount: float = 0.0

@dataclass
class RequestItem:
    request_id: str
    user_id: str
    request_date: str
    request_type: str
    requested_amount: float
    desired_completion_date: str
    allows_partial_payment: bool
    request_text: str

@dataclass
class PlanCandidate:
    method: str # full_payment | partial_payment | installments | wait | not_recommended
    affordability_status: str # affordable_now | affordable_with_plan | affordable_later | not_affordable
    payment_plan: str # YYYY-MM-DD:amt|... or 'none'
    schedule: List[Tuple[str, float]]
    completes_by_deadline: bool
    spending_changes: List[str] = field(default_factory=list)
    total_amount_paid: float = 0.0
    start_date: str = '9999-12-31'
    num_payments: int = 0
    payment_option_id: Optional[str] = None
    is_safe: bool = False

@dataclass
class PredictionResult:
    request_id: str
    amount_safe_to_pay: float
    affordability_status: str
    recommended_payment_method: str
    payment_plan: str
    earliest_date_for_full_payment: str
    spending_changes_needed: str
    decision_explanation: str

    def to_csv_row(self) -> dict:
        return {
            'request_id': self.request_id,
            'amount_safe_to_pay': self.amount_safe_to_pay,
            'affordability_status': self.affordability_status,
            'recommended_payment_method': self.recommended_payment_method,
            'payment_plan': self.payment_plan,
            'earliest_date_for_full_payment': self.earliest_date_for_full_payment,
            'spending_changes_needed': self.spending_changes_needed,
            'decision_explanation': self.decision_explanation
        }
