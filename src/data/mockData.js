/**
 * Mock Data Module for "Buy or Wait?"
 * Localized for Indian Rupee (INR / ₹) with realistic personal finance benchmarks.
 */

export { verdictMap, formatINR } from '../theme/tokens';

export const userFinancialProfile = {
  currentBalance: 1240000,      // ₹12,40,000
  safetyFloor: 800000,          // ₹8,00,000
  availableToSpend: 440000,     // ₹4,40,000
  currency: 'INR',
  currencySymbol: '₹',
  monthlyNetIncome: 340000,     // ₹3,40,000
  monthlyFixedExpenses: 185000, // ₹1,85,000
  lastUpdated: '2026-09-12T10:00:00Z',
};

export const exampleQueries = [
  { text: 'a round-trip to Tokyo for ₹2,80,000', amount: 280000, category: 'Travel' },
  { text: 'Sony WH-1000XM5 headphones for ₹29,990', amount: 29990, category: 'Purchase' },
  { text: 'MacBook Pro M3 Max for ₹3,49,900', amount: 349900, category: 'Purchase' },
  { text: 'Full-stack AI & Cloud Bootcamp for ₹65,000', amount: 65000, category: 'Education' },
  { text: 'Royal Enfield Himalayan Down Payment for ₹95,000', amount: 95000, category: 'Debt' },
  { text: 'Ergonomic Herman Miller Chair for ₹1,15,000', amount: 115000, category: 'Purchase' },
];

export const categories = [
  'Purchase',
  'Travel',
  'Education',
  'Family',
  'Debt',
  'Investment',
  'Housing',
  'Emergency',
  'Other',
];

export const sampleRequest = {
  id: 'req-tokyo-2026',
  title: 'Tokyo Trip (Flights & Hotel)',
  emoji: '✈️',
  amount: 280000,
  category: 'Travel',
  date: 'Sep 12, 2026',
  verdict: 'affordable_with_plan',
  verdictHeadline: 'Affordable across 6 scheduled payments.',
  summary: 'A structured payment plan preserves your ₹8,00,000 cash reserve while absorbing the full ₹2,80,000 cost safely over 90 days.',
  stats: {
    safeToPayNow: 50000,
    totalCost: 280000,
    fullPaymentBy: 'Dec 10, 2026',
    installmentsCount: 6,
    recommendedPlan: '6 Bi-weekly Installments',
    ctaLabel: 'Set Up Installments',
  },
  whyRecommendation: {
    plainLanguage:
      'Paying the full ₹2,80,000 upfront on Sep 12 would immediately drop your liquid buffer dangerously close to the safety floor before your month-end SIP and EMI commitments execute. Spreading payments across 6 installments of ~₹45,000–₹50,000 synchronized with your Oct 1, Nov 1, and Dec 1 salary credits ensures your lowest balance never falls below ₹11,53,000—maintaining an impenetrable ₹3,53,000 surplus above your safety threshold at all times.',
    tiles: [
      { label: 'Minimum Buffer', value: '₹3,53,000', sub: 'Above safety floor' },
      { label: 'Cashflow Impact', value: '4.1%', sub: 'Of monthly income' },
      { label: 'Safety Margin', value: '100%', sub: 'Zero floor violations' },
      { label: 'Salary Sync', value: 'Optimal', sub: 'Offset by +₹3,40,000 inflow' },
    ],
  },
};

// 6 installments: ₹50,000, ₹45,000, ₹45,000, ₹45,000, ₹45,000, ₹50,000 (Aug 25 – Dec 10)
export const sampleInstallments = [
  {
    id: 'inst-1',
    number: 1,
    amount: 50000,
    dueDate: 'Aug 25, 2026',
    status: 'paid',
    optionId: 'OPT-INR-01',
    method: 'Auto-Debit · HDFC Salary A/c (*4821)',
  },
  {
    id: 'inst-2',
    number: 2,
    amount: 45000,
    dueDate: 'Sep 08, 2026',
    status: 'paid',
    optionId: 'OPT-INR-02',
    method: 'Auto-Debit · HDFC Salary A/c (*4821)',
  },
  {
    id: 'inst-3',
    number: 3,
    amount: 45000,
    dueDate: 'Sep 22, 2026',
    status: 'upcoming',
    optionId: 'OPT-INR-03',
    method: 'Scheduled · HDFC Salary A/c (*4821)',
  },
  {
    id: 'inst-4',
    number: 4,
    amount: 45000,
    dueDate: 'Oct 06, 2026',
    status: 'upcoming',
    optionId: 'OPT-INR-04',
    method: 'Scheduled · HDFC Salary A/c (*4821)',
  },
  {
    id: 'inst-5',
    number: 5,
    amount: 45000,
    dueDate: 'Oct 20, 2026',
    status: 'upcoming',
    optionId: 'OPT-INR-05',
    method: 'Scheduled · HDFC Salary A/c (*4821)',
  },
  {
    id: 'inst-6',
    number: 6,
    amount: 50000,
    dueDate: 'Dec 10, 2026',
    status: 'upcoming',
    optionId: 'OPT-INR-06',
    method: 'Final Installment · HDFC Salary A/c (*4821)',
  },
];

// 10 forecast points from Sep 12 to Dec 10 in INR
// Balance range: ₹11,53,000 to ₹19,23,000
// Salary deposits (+₹3,40,000) on Oct 1, Nov 1, Dec 1
export const forecastPoints = [
  { date: 'Sep 12', balance: 1240000, event: 'Today (Initial Balance)', isPaymentDate: false },
  { date: 'Sep 22', balance: 1195000, event: 'Tokyo Trip Installment #3 (-₹45,000)', isPaymentDate: true, paymentAmount: 45000 },
  { date: 'Oct 01', balance: 1475000, event: 'Monthly Salary (+₹3,40,000) - Rent (-₹60,000)', isIncome: true, isPaymentDate: false },
  { date: 'Oct 06', balance: 1430000, event: 'Tokyo Trip Installment #4 (-₹45,000)', isPaymentDate: true, paymentAmount: 45000 },
  { date: 'Oct 20', balance: 1385000, event: 'Tokyo Trip Installment #5 (-₹45,000)', isPaymentDate: true, paymentAmount: 45000 },
  { date: 'Nov 01', balance: 1675000, event: 'Monthly Salary (+₹3,40,000) - Fixed EMIs (-₹50,000)', isIncome: true, isPaymentDate: false },
  { date: 'Nov 15', balance: 1590000, event: 'Mid-month utilities & dining (-₹85,000)', isPaymentDate: false },
  { date: 'Dec 01', balance: 1923000, event: 'Monthly Salary (+₹3,40,000) & Annual Bonus Preview', isIncome: true, isPaymentDate: false },
  { date: 'Dec 08', balance: 1873000, event: 'Year-end festival shopping buffer (-₹50,000)', isPaymentDate: false },
  { date: 'Dec 10', balance: 1823000, event: 'Tokyo Trip Final Installment #6 (-₹50,000)', isPaymentDate: true, paymentAmount: 50000 },
];

// Spending changes in INR
export const initialSpendingChanges = [
  {
    id: 'spend-1',
    label: 'Pause Netflix Premium',
    subLabel: 'Unused for 22 days · Can resume anytime',
    monthlySavings: 649,
    category: 'Subscription',
    icon: '📺',
  },
  {
    id: 'spend-2',
    label: 'Switch Spotify to Family/Duo',
    subLabel: 'Split subscription with household',
    monthlySavings: 119,
    category: 'Subscription',
    icon: '🎵',
  },
  {
    id: 'spend-3',
    label: 'Cook 2 Dinners at Home Weekly',
    subLabel: 'Trim discretionary dining & Swiggy/Zomato orders',
    monthlySavings: 8000,
    category: 'Dining',
    icon: '🍽️',
  },
];

// Upcoming timeline events for Dashboard in INR
export const upcomingEvents = [
  { id: 'ev-1', date: 'Sep 22', label: 'Tokyo Trip Installment #3', amount: -45000, isIncome: false, category: 'Travel' },
  { id: 'ev-2', date: 'Sep 28', label: 'Electricity & High-speed Fiber', amount: -3850, isIncome: false, category: 'Utilities' },
  { id: 'ev-3', date: 'Oct 01', label: 'Monthly Salary Credit', amount: 340000, isIncome: true, category: 'Income' },
  { id: 'ev-4', date: 'Oct 06', label: 'Tokyo Trip Installment #4', amount: -45000, isIncome: false, category: 'Travel' },
  { id: 'ev-5', date: 'Oct 15', label: 'Comprehensive Car Insurance', amount: -18500, isIncome: false, category: 'Transport' },
  { id: 'ev-6', date: 'Nov 01', label: 'Monthly Salary Credit', amount: 340000, isIncome: true, category: 'Income' },
  { id: 'ev-7', date: 'Dec 01', label: 'Monthly Salary Credit', amount: 340000, isIncome: true, category: 'Income' },
];

// History: 7 items in INR covering all four verdict states
export const historyItems = [
  {
    id: 'hist-1',
    title: 'Round-trip to Tokyo (Sep-Dec)',
    emoji: '✈️',
    amount: 280000,
    date: 'Sep 12, 2026',
    category: 'Travel',
    verdict: 'affordable_with_plan',
    verdictLabel: 'Affordable with Plan',
    notes: '6 bi-weekly installments approved',
  },
  {
    id: 'hist-2',
    title: 'Sony WH-1000XM5 Headphones',
    emoji: '🎧',
    amount: 29990,
    date: 'Sep 04, 2026',
    category: 'Purchase',
    verdict: 'affordable_now',
    verdictLabel: 'Affordable Now',
    notes: 'Paid in full from monthly liquid buffer',
  },
  {
    id: 'hist-3',
    title: 'MacBook Pro M3 Max (64GB)',
    emoji: '💻',
    amount: 349900,
    date: 'Aug 29, 2026',
    category: 'Purchase',
    verdict: 'affordable_later',
    verdictLabel: 'Affordable Later',
    notes: 'Waiting for Q3 performance incentive bonus',
  },
  {
    id: 'hist-4',
    title: 'Royal Enfield Himalayan Down Payment',
    emoji: '🏍️',
    amount: 95000,
    date: 'Aug 20, 2026',
    category: 'Debt',
    verdict: 'affordable_now',
    verdictLabel: 'Affordable Now',
    notes: 'Zero-cost financing option selected',
  },
  {
    id: 'hist-5',
    title: 'Swiss Alps & European Tour',
    emoji: '🏔️',
    amount: 520000,
    date: 'Aug 18, 2026',
    category: 'Travel',
    verdict: 'not_affordable',
    verdictLabel: 'Not Affordable',
    notes: 'Breaches ₹8,00,000 floor by ₹1,80,000 on day 35',
  },
  {
    id: 'hist-6',
    title: 'Executive AI & Systems Leadership Course',
    emoji: '📚',
    amount: 85000,
    date: 'Aug 10, 2026',
    category: 'Education',
    verdict: 'affordable_now',
    verdictLabel: 'Affordable Now',
    notes: 'Skill development tax-advantaged allowance',
  },
  {
    id: 'hist-7',
    title: 'Emergency Dental Surgery & Crown',
    emoji: '🦷',
    amount: 45000,
    date: 'Jul 14, 2026',
    category: 'Emergency',
    verdict: 'affordable_with_plan',
    verdictLabel: 'Affordable with Plan',
    notes: '3 monthly interest-free provider payments',
  },
];

// Active plans for Dashboard overview in INR
export const activePlans = [
  {
    id: 'plan-1',
    title: 'Tokyo Trip (Flights & Stay)',
    totalAmount: 280000,
    paidAmount: 95000,
    totalInstallments: 6,
    paidInstallments: 2,
    nextDue: 'Sep 22, 2026 (₹45,000)',
    progress: 34,
  },
  {
    id: 'plan-2',
    title: 'Emergency Dental Procedure',
    totalAmount: 45000,
    paidAmount: 30000,
    totalInstallments: 3,
    paidInstallments: 2,
    nextDue: 'Sep 30, 2026 (₹15,000)',
    progress: 67,
  }
];
