# `q_bank` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
`q_bank` is the **Financial & Bank Statement Forensic Engine** of ForensiQ.
It provides:
1. **Statement Ingestion & OCR/PDF Parsing:** Automated extraction of bank transaction ledgers from major banking formats (HDFC, ICICI, SBI, Axis, HSBC, etc.).
2. **Suspicious Transaction Screening:** Algorithmic flagging for structuring/smurfing, circular round-tripping, high-value debits, and tax-haven remittances.
3. **Interactive Forensic Grid:** Tabulator-powered transaction ledger with custom risk gauges, direction pills, and modal case dossiers.

---

## 2. Directory Structure
```
apps/q_bank/
├── apps.py            # AppConfig with module metadata for landing page
├── models.py          # BankAccount, BankTransaction, WatchlistRule
├── views.py           # Dashboard, ledger, statement upload views
├── services.py        # Statement parser, rule evaluator, risk scoring service
├── urls.py            # Routing for /q_bank/
├── templates/q_bank/  # Dashboard & audit ledger templates
├── INSTRUCTION.md     # Developer guide (this file)
├── SCHEMA.md          # Database models and Tabulator table columns spec
└── USER_GUIDE.md      # Investigator operational manual
```

---

## 3. Strict Rules for Interns & Vibe-Coding

> [!IMPORTANT]
> **Rule 1: Always Inherit from `ForensicBaseModel`**
> All models in `models.py` must inherit from `core.models.ForensicBaseModel`.

> [!IMPORTANT]
> **Rule 2: Currency & Numbers Formatting**
> Monetary amounts must always be stored as `DecimalField(max_digits=18, decimal_places=2)`. In Tabulator formatters, use Indian Rupee currency format (`new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' })`).

> [!IMPORTANT]
> **Rule 3: Use Standard Cotton Layout**
> All views must wrap inside `<c-base title="...">` and use `<c-stat_card>`, `<c-filter_bar>`, and `<c-data_grid>` components.
