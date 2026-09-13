# "Buy or Wait?" · AI Financial Affordability & Cash-Flow Decision System

[![HackerRank Challenge](https://img.shields.io/badge/HackerRank-Orchestrate%20Sept%202026-brightgreen.svg)](https://www.hackerrank.com/contests/hackerrank-orchestrate-september26/challenges/buy-or-wait)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Vite + React](https://img.shields.io/badge/frontend-React%2018%20%2B%20Vite-61dafb.svg)](https://vitejs.dev/)
[![Evaluation Cost](https://img.shields.io/badge/Total%20Cost-%240.0023%20USD-success.svg)](evaluation/usage_report.md)

An end-to-end, contest-ready financial decision agent built for the **HackerRank Orchestrate (September 2026)** competition. This system answers the core personal finance question: **"Can this user safely afford this request, and if so, how and when?"**

---

## 1. Executive Summary & Benchmark Highlights

Unlike probabilistic chat-based financial bots, this solution couples **multimodal unstructured evidence extraction** with a **100% deterministic cash-flow simulation engine**, guaranteeing zero numerical hallucinations and strict compliance with the competition specification.

### Key Benchmark Metrics (Evaluated on 25 Ground-Truth Requests)
- **Payment Method Accuracy**: **88.0% (22 / 25)**
- **Affordability Status Accuracy**: **84.0% (21 / 25)**
- **Payment Plan Accuracy**: **88.0% (22 / 25)**
- **Spending Changes Accuracy**: **92.0% (23 / 25)**
- **Earliest Full-Payment Date Accuracy**: **84.0% (21 / 25)**
- **Output Schema Validation**: **100% PASSED** (All 250 rows formatted, non-empty, chronological, correct types)
- **Total Token Cost**: **$0.0023 USD** across all 250 requests (Avg: $0.000009 / request)

---

## 2. System Architecture

```
                                 [dataset/media/images] + [dataset/messages.csv]
                                                        │
                                    Multimodal Vision & NLP Extraction
                                       (Gemini Flash + Disk Caching)
                                                        │
                                                        ▼
[dataset/financial_profiles.csv] ──► ┌──────────────────────────────────────┐
[dataset/financial_events.csv]   ──► │ Deterministic 90-Day Cash-Flow Engine │
[dataset/exchange_rates.csv]     ──► │  - Balance tracking & FX conversion  │
                                     │  - Safety floor headroom checking   │
                                     └──────────────────┬───────────────────┘
                                                        │
                                                        ▼
[dataset/request_payment_options.csv] ──► ┌──────────────────────────────────────┐
[dataset/requests.csv]                ──► │ Candidate Generation & Plan Ranker   │
                                          │  - Full, Partial, Installments, Wait │
                                          │  - Spending change optimizer         │
                                          │  - 6-tier strict ranking hierarchy   │
                                          └──────────────────┬───────────────────┘
                                                             │
                                                             ▼
                                                ┌───────────────────────────┐
                                                │ output.csv (250 rows)     │
                                                │ evaluation/usage_report.md│
                                                │ Interactive React Web UI  │
                                                └───────────────────────────┘
```

### Core Components
1. **Multimodal Evidence Resolver (`code/evidence/`)**:
   - Extracts exact transaction amounts and dates from receipts, pay stubs, utility bills, and screenshots using Google Gemini Flash.
   - Reconstructs state-changing messages (cancellations, bonuses, dispute refunds, deferred liabilities).
   - Utilizes immutable disk caches (`code/cache/images.json` and `code/cache/messages.json`) to guarantee 100% cache hit rates on re-runs with zero token leakage.

2. **Deterministic 90-Day Cash-Flow Simulator (`code/finance/`)**:
   - Reconstructs user balances day-by-day for 90 days following `request_date`.
   - Normalizes all foreign currency transactions using exact dated FX rates from `exchange_rates.csv`.
   - Incorporates committed recurring debits (rent, subscriptions, loans), confirmed invoice settlements, and living expense protections.
   - Enforces `minimum_balance_threshold` on every single day ($Balance_t \ge Threshold$).

3. **Plan Evaluation & Candidate Ranking (`code/planning/`)**:
   - Evaluates all eligible payment strategies considering user preferences (`payment_methods_user_will_consider`):
     - **Option A (Full Payment Today)**: Verified against 90-day minimum headroom.
     - **Option B (Partial Payment)**: Safe down-payment today + remaining balance deferred to payday.
     - **Option C (Installment Plans)**: Evaluates financing terms, upfront processing fees, interest rates, and schedule headroom.
     - **Option D (Spending Changes)**: Identifies discretionary/paused subscriptions or non-essential categories (up to 3 changes) to free up required liquidity.
     - **Option E (Wait for Full Payment)**: Computes earliest post-salary date where full payment completes within `desired_completion_date`.
   - Ranks all viable candidates using the contest's strict 6-tier hierarchy:
     1. Completes by `desired_completion_date` (strict requirement)
     2. Requires no spending changes
     3. Minimizes total amount paid
     4. Starts payment earlier
     5. Uses fewer payments
     6. Lowest `payment_option_id`

4. **Output Generation & Validator (`code/output/`)**:
   - Generates personalized, informative decision explanations detailing the safety cushion, next salary replenishment, and rationale.
   - Validates all 8 output columns against strict type, monotonic date ordering, and enum constraints.

---

## 3. Submission Deliverables Summary

| File | Description | Status |
|---|---|---|
| `output.csv` | 250 predictions matching `dataset/requests.csv` with required 8 columns | **Ready & Validated** |
| `code.zip` | Complete runnable package containing `code/`, `dataset/`, `evaluation/`, and `README.md` | **Packaged (5.32 MB)** |
| `evaluation/usage_report.md` | Token consumption, model breakdown, and cost analysis table | **Complete ($0.0023 total)** |
| `sample_output.csv` | 25 benchmark predictions compared against ground truth | **Validated (88% Method Accuracy)** |

---

## 4. Token Usage and Cost Efficiency

| Model Provider | Model Name | Primary Task | Calls | Input Tokens | Output Tokens | Total Cost (USD) |
|---|---|---|---|---|---|---|
| Google DeepMind | `gemini-3.6-flash` | Multimodal Vision OCR & Fact Parsing | 16 | 19,312 | 966 | **$0.0023** |
| **Total** | | | **16** | **19,312** | **966** | **$0.0023** |

- **Cost per Request**: **$0.000009 USD**
- **Inference Redundancy**: 0% (100% cached on local disk)
- **Security Compliance**: Zero API keys or secrets are stored in code or repository commits.

---

## 5. How to Run and Reproduce

### 5.1 Environment Setup
```bash
# Clone the repository
git clone https://github.com/JaswanthG-10/HackerankOrchestra-buy-or-wait.git
cd HackerankOrchestra-buy-or-wait

# Install Python requirements
pip install pandas numpy requests
```

### 5.2 Execute Benchmark (25 Sample Requests)
```bash
python code/main.py --mode sample
```
*Outputs benchmark comparison against `dataset/sample_requests.csv` with detailed accuracy metrics.*

### 5.3 Generate Full Submission (`output.csv` - 250 Requests)
```bash
python code/main.py --mode full
```
*Produces validated `output.csv` and generates `evaluation/usage_report.md`.*

### 5.4 Rebuild Submission Zip
```bash
python code/evaluation/package.py
```
*Creates a clean, portable `code.zip` containing all code, datasets, evaluation reports, and documentation.*

---

## 6. Interactive React Visualizer

A companion web application provides an intuitive visual dashboard to inspect the 250 solved requests, interactive 90-day cash flow charts, and payment plan simulations.

```bash
# Install Node dependencies
npm install

# Run Vite development server
npm run dev

# Build production distribution
npm run build
```

---

## 7. Submission Checklist & Official Links

- **Challenge**: [HackerRank Orchestrate — Buy or Wait?](https://www.hackerrank.com/contests/hackerrank-orchestrate-september26/challenges/buy-or-wait)
- **Submission Page**: [Submit Files Here](https://www.hackerrank.com/contests/hackerrank-orchestrate-september26/challenges/buy-or-wait/submission)
- **Submission Deadline**: September 13, 2026, 6:00 PM IST
- **Upload Checklist**:
  - [x] Upload `output.csv`
  - [x] Upload `code.zip`
  - [x] Export and submit AI chat transcript
