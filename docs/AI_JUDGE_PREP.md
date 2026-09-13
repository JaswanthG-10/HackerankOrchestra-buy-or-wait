# AI Judge Interview Preparation & Technical Notes

## 1. What problem does the project solve?
"Buy or Wait?" is an intelligent personal financial decision engine. It evaluates whether a user can safely afford a purchase today, pay in installments, defer the purchase until a safe date, or unlock affordability by stopping or reducing flexible recurring expenses—all while guaranteeing that their account balance never breaches their required minimum balance over a strict 90-day horizon.

## 2. Why use AI at all?
AI (multimodal vision + text processing) is used exclusively for state reconstruction from unstructured user evidence:
- Extracting exact dates, amounts, merchant details, and transaction statuses from receipt screenshots and banking proof images.
- Structuring customer chat messages and natural language updates into deterministic financial rules.
AI is NOT used for cash calculations or financial decision logic.

## 3. Why not ask Gemini to make the final decision?
LLMs are probabilistic engines subject to hallucination, floating-point arithmetic errors, and inconsistent decision boundaries. Financial safety requires 100% deterministic precision. We isolate AI to information extraction, and pass all extracted facts to a deterministic 90-day financial simulator and optimizer.

## 4. How are images handled?
Images (receipts, bill statements, bank notices) are processed using `google-genai` multimodal vision. Extracted attributes (`amount`, `settlement_date`, `status`, `direction`, `category`) are validated, normalized, and cached in `dataset/image_cache.json` for instant, 100% reproducible execution.

## 5. How are pending credits treated?
Pending credits (e.g., unconfirmed refunds, pending bonus payouts, unverified freelance invoices) are strictly EXCLUDED from cash flow projections until explicitly settled or confirmed by proof. This prevents overestimating available funds and risking balance breaches.

## 6. How are pending debits treated?
Pending debits (e.g., pending card authorizations, pending bill payments) represent committed future outflows. They are RESERVED on Day 0 or their expected settlement date, reducing immediate headroom to prevent double spending.

## 7. How is recurrence detected?
Recurrence is inferred strictly from historical settled transactions using interval consistency checks:
- 6–8 days: Weekly
- 13–16 days: Bi-weekly
- 26–33 days (or matching calendar day): Monthly
- Category-level living expense cadences (groceries, transport, dining) are tracked to capture multi-occurrence monthly spending without inventing arbitrary fallback recurrence.

## 8. How are linked transactions resolved?
Linked transactions (e.g., `scheduled -> pending -> settled`, authorization hold -> settled purchase, failed -> retry -> settled, refund requests) are collapsed into a single effective obligation using Directed Acyclic Graph (DAG) traversal in `code/finance/lifecycle.py`. Obsolete intermediate or cancelled records are pruned to eliminate double-counting.

## 9. What is amount_safe_to_pay?
`amount_safe_to_pay` is the maximum cash outlay the user can execute on Day 0 such that their projected available balance remains $\ge \text{minimum\_balance\_to\_keep}$ on every single day over the 90-day simulation window.

## 10. Why can safe amount differ from final affordable amount?
`amount_safe_to_pay` measures unadjusted baseline headroom on Day 0. If the requested purchase exceeds baseline safe amount, an optimal spending-change plan (stopping/reducing flexible subscriptions) or installment schedule can increase future headroom, enabling full purchase completion safely.

## 11. How are installment plans selected?
Installment options provided in `dataset/payment_options.csv` are evaluated by running 90-day cash flow simulations with the exact installment dates and amounts. Plans are filtered for 100% safety, and the candidate with the fewest installment months and lowest interest fee is selected according to problem tier rules.

## 12. How are spending changes selected?
Spending change candidates are filtered for user-permitted, non-protected, flexible categories (`stoppable`, `reducible`). Combinations of up to 3 changes are ranked by minimal disruption (prefer 1 change > 2 > 3, lowest total reduction). Binary search determines the minimal required expense reduction that satisfies the 90-day balance constraint.

## 13. How does the 90-day simulator work?
`run_90_day_simulation` constructs a daily cash timeline for $t \in [0, 90]$ days by aggregating:
1. Resolved non-duplicate historical and scheduled financial events.
2. Inferred recurring obligations.
3. Salary schedule and confirmed updates.
4. Active payment schedule.
It tracks cumulative daily balance and computes minimum projected headroom: $\min_t (\text{balance}_t - \text{minimum\_balance\_to\_keep})$.

## 14. How do you prevent prompt injection?
Image extraction and message parsing use strict JSON schema enforcement with Pydantic/dataclasses. Unstructured text inputs are parsed purely into strongly-typed parameters without directly executing dynamic instructions or prompt code.

## 15. How do you guarantee reproducibility?
- Deterministic 90-day simulation engine.
- Image extraction facts cached in `dataset/image_cache.json` and message rules in `dataset/message_cache.json`.
- Zero runtime LLM variance during decision execution (`python code/main.py --mode sample` runs 100% deterministically in under 3 seconds).

## 16. What was the hardest technical issue?
Linked-event lifecycle chaining and deduplication between explicit future scheduled events and inferred recurring obligations. Resolving multi-state transaction graphs (`scheduled -> pending -> settled`) without double-counting required formal graph traversal and chronology sorting.

## 17. What would you improve with more time?
1. Dynamic seasonal expenditure adjustments for utility peaks and holiday travel.
2. Multi-currency portfolio optimization with real-time forward exchange rate hedging.
3. Interactive visual cash-flow scenario builder for real-time customer goal modeling.
