/**
 * Data Module for "Buy or Wait?" UI
 * Wires realOutput.json (250 real solver predictions) directly into the UI.
 */

import realOutput from './realOutput.json';
export { verdictMap, formatINR } from '../theme/tokens';

export const realRequests = realOutput.map((item) => ({
  id: item.request_id,
  userId: item.user_id,
  title: item.request_text,
  amount: item.requested_amount,
  currency: item.home_currency || 'INR',
  date: item.request_date,
  desiredCompletionDate: item.desired_completion_date,
  verdict: item.affordability_status,
  recommendedMethod: item.recommended_payment_method,
  paymentPlan: item.payment_plan,
  earliestFullPaymentDate: item.earliest_date_for_full_payment,
  spendingChangesNeeded: item.spending_changes_needed,
  summary: item.decision_explanation,
  currentBalance: item.current_available_balance,
  minimumKeep: item.minimum_balance_to_keep,
  stats: {
    safeToPayNow: item.amount_safe_to_pay,
    totalCost: item.requested_amount,
    fullPaymentBy: item.earliest_date_for_full_payment || item.desired_completion_date,
    recommendedPlan: item.payment_plan !== 'none' ? item.payment_plan : 'No safe option available',
    ctaLabel: item.affordability_status === 'affordable_now' ? 'Proceed with Full Payment' : 
             item.affordability_status === 'affordable_with_plan' ? 'Apply Recommended Plan' :
             item.affordability_status === 'affordable_later' ? 'Schedule for Payday' : 'Decline Request'
  },
  whyRecommendation: {
    plainLanguage: item.decision_explanation,
    tiles: [
      { label: 'Minimum Buffer', value: `${item.home_currency || ''} ${item.minimum_balance_to_keep?.toLocaleString()}`, sub: 'Protected floor' },
      { label: 'Safe Amount Today', value: `${item.home_currency || ''} ${item.amount_safe_to_pay?.toLocaleString()}`, sub: 'Day 0 headroom' },
      { label: 'Payment Method', value: item.recommended_payment_method?.replace('_', ' ').toUpperCase(), sub: 'Optimal strategy' },
      { label: 'Spending Changes', value: item.spending_changes_needed === 'none' ? 'None Required' : item.spending_changes_needed, sub: 'Discretionary' }
    ]
  }
}));

export const userFinancialProfile = {
  currentBalance: realOutput[0]?.current_available_balance || 1240000,
  safetyFloor: realOutput[0]?.minimum_balance_to_keep || 800000,
  availableToSpend: (realOutput[0]?.current_available_balance || 1240000) - (realOutput[0]?.minimum_balance_to_keep || 800000),
  currency: realOutput[0]?.home_currency || 'INR',
  monthlyNetIncome: 340000,
  monthlyFixedExpenses: 185000,
  lastUpdated: '2026-09-13T10:00:00Z',
};

export const historyItems = realRequests;
export const sampleRequest = realRequests[0];

export const sampleInstallments = [
  {
    id: 'inst-1',
    number: 1,
    amount: Math.round(sampleRequest.amount / 3),
    dueDate: sampleRequest.date,
    status: 'paid',
    optionId: 'OPT-01',
    method: 'Auto-Debit · Primary Account',
  },
  {
    id: 'inst-2',
    number: 2,
    amount: Math.round(sampleRequest.amount / 3),
    dueDate: '2026-10-15',
    status: 'upcoming',
    optionId: 'OPT-02',
    method: 'Scheduled · Primary Account',
  },
  {
    id: 'inst-3',
    number: 3,
    amount: Math.round(sampleRequest.amount / 3),
    dueDate: '2026-11-15',
    status: 'upcoming',
    optionId: 'OPT-03',
    method: 'Scheduled · Primary Account',
  },
];

export const initialSpendingChanges = [
  {
    id: 'spend-1',
    label: 'Pause Streaming Subscription',
    subLabel: 'Can resume anytime after purchase',
    monthlySavings: 649,
    category: 'Subscription',
    icon: '📺',
  },
  {
    id: 'spend-2',
    label: 'Reduce Dining & Takeout',
    subLabel: 'Trim discretionary dining spend',
    monthlySavings: 8000,
    category: 'Dining',
    icon: '🍽️',
  },
];

export const upcomingEvents = realOutput.slice(0, 5).map((item, idx) => ({
  id: `ev-${idx}`,
  date: item.request_date,
  label: item.request_text.slice(0, 40) + '...',
  amount: -item.requested_amount,
  isIncome: false,
  category: item.request_type
}));

export const activePlans = [
  {
    id: 'plan-1',
    title: realRequests[0].title.slice(0, 40) + '...',
    totalAmount: realRequests[0].amount,
    paidAmount: realRequests[0].stats.safeToPayNow,
    totalInstallments: 3,
    paidInstallments: 1,
    nextDue: realRequests[0].desiredCompletionDate,
    progress: 33,
  }
];

export const forecastPoints = Array.from({ length: 90 }, (_, i) => {
  const dt = new Date(Date.now() + i * 86400000);
  const dateStr = dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  const baseBal = userFinancialProfile.currentBalance;
  const floor = userFinancialProfile.safetyFloor;
  const wiggle = Math.sin(i / 5) * 15000 + (i % 30 === 0 ? 340000 : 0) - (i % 14 === 0 ? 45000 : 0);
  return {
    day: `Day ${i + 1}`,
    date: dateStr,
    balance: Math.max(floor + 50000, baseBal + wiggle),
    floor: floor,
    projected: Math.max(floor + 20000, baseBal + wiggle - 50000)
  };
});

export const exampleQueries = realOutput.slice(0, 6).map((item) => ({
  text: item.request_text,
  amount: item.requested_amount,
  category: item.request_type
}));

export const categories = [
  'purchase',
  'family_transfer',
  'investment',
  'emergency',
  'bill_payment',
  'debt_repayment'
];
