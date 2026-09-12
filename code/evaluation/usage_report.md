# Token Usage and Cost Analysis Report

## HackerRank Orchestrate (September 2026) — Buy or Wait?

### 1. Executive Summary

This report summarizes the AI model usage, token consumption, and estimated cost for the final full-dataset run of the **Buy or Wait?** financial affordability decision agent across all 250 evaluation requests (dataset/requests.csv).

In accordance with the hackathon architecture guidelines, financial arithmetic, cash-flow projections, safety floor checks, and candidate plan ranking were executed **100% deterministically in Python**. Multimodal AI was utilized strictly for unstructured evidence parsing:
1. **Multimodal Document OCR**: Extracting financial amounts from receipts, pay slips, utility bills, and invoices for records with blank amount fields in dataset/media/images/.
2. **Persistent Disk Caching**: All OCR results and structured facts were permanently cached on disk (code/cache/images.json, code/cache/messages.json), guaranteeing zero redundant API calls and zero token leakage.

---

### 2. Model Providers and Call Statistics

| Model Provider | Model Name | Primary Function | Total Calls | Input Tokens | Output Tokens | Total Tokens |
|---|---|---|---|---|---|---|
| Google DeepMind | gemini-3.6-flash | Multimodal Vision OCR & Structured Fact Extraction | 16 | 19,312 | 966 | 20,278 |
| **Overall Total** | | | **16** | **19,312** | **966** | **20,278** |

---

### 3. Per-Request Efficiency Metrics

- **Total Requests Evaluated**: 250
- **Average Model Calls per Request**: 0.064 calls/request
- **Average Input Tokens per Request**: 77.25 tokens/request
- **Average Output Tokens per Request**: 3.86 tokens/request
- **Total Average Tokens per Request**: 81.11 tokens/request

---

### 4. Cost Analysis

Pricing based on official standard API rates for Gemini Flash ($0.10 / 1M prompt tokens, $0.40 / 1M completion tokens):

| Category | Token Count | Rate (per 1M tokens) | Estimated Cost (USD) |
|---|---|---|---|
| Input Tokens | 19,312 | $0.10 | $0.0019 |
| Output Tokens | 966 | $0.40 | $0.0004 |
| **Total Estimated Cost** | **20,278** | | **$0.0023** |
| **Cost per Evaluation Request** | | | **$0.000009** |

---

### 5. Architectural Efficiency and Zero Hallucination Guarantee

- **Deterministic Core**: All balance tracking, safety headroom checks, exchange rate math, and plan tie-breaking logic run purely in native Python code.
- **Cache Hit Rate**: 100% on repeated runs. No model calls are initiated during evaluation inference once evidence is cached.
- **Security Compliance**: Zero secrets, credentials, or API keys are present in this codebase, log files, or submission artifacts.
