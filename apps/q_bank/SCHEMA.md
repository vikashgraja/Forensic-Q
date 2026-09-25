# `q_bank` — Database Schema & ERD Specifications

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// Q-Bank Financial Forensic Ledger Schema
// dbdiagram.io specification
// ==========================================

Table bank_accounts {
  id uuid [pk, default: `uuid4()`]
  account_number varchar(64) [not null, unique]
  bank_name varchar(128) [not null]
  account_holder varchar(255) [not null]
  ifsc_code varchar(32)
  currency varchar(8) [default: 'INR']
  is_target_entity boolean [default: false]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]

  Note: 'Target bank accounts and counterparties under forensic audit'
}

Table bank_transactions {
  id uuid [pk, default: `uuid4()`]
  account_id uuid [ref: > bank_accounts.id]
  txn_ref varchar(128) [not null, unique]
  txn_date timestamp [not null]
  party_name varchar(255) [not null]
  party_account_mask varchar(64)
  category varchar(128) [note: 'Shell Wire, Vendor Payment, Loan, etc.']
  direction varchar(8) [note: 'IN (Credit) or OUT (Debit)']
  amount decimal(18,2) [not null]
  risk_score int [default: 0, note: 'Score 0 - 100']
  risk_level varchar(16) [default: 'Low', note: 'Low, Medium, High']
  status varchar(32) [default: 'Cleared', note: 'Cleared, Under Review, Flagged, Escalated']
  flag_reason text [note: 'Detailed forensic rationale']
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]

  Note: 'Individual bank transactions with risk metrics and forensic flags'
}

Table watchlist_rules {
  id uuid [pk, default: `uuid4()`]
  rule_name varchar(128) [not null]
  keyword varchar(128) [not null]
  risk_weight int [default: 50]
  category varchar(64)
  is_active boolean [default: true]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]

  Note: 'Customizable watchlist rules and keyword flags per investigation'
}
```

---

## 2. Django ORM Models

```python
from django.db import models
from core.models import ForensicBaseModel


class BankAccount(ForensicBaseModel):
    account_number = models.CharField(max_length=64, unique=True, db_index=True)
    bank_name = models.CharField(max_length=128)
    account_holder = models.CharField(max_length=255)
    ifsc_code = models.CharField(max_length=32, blank=True)
    currency = models.CharField(max_length=8, default="INR")
    is_target_entity = models.BooleanField(default=False)


class BankTransaction(ForensicBaseModel):
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="transactions")
    txn_ref = models.CharField(max_length=128, unique=True, db_index=True)
    txn_date = models.DateTimeField(db_index=True)
    party_name = models.CharField(max_length=255)
    party_account_mask = models.CharField(max_length=64, blank=True)
    category = models.CharField(max_length=128)
    direction = models.CharField(max_length=8, choices=[("IN", "Credit"), ("OUT", "Debit")])
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    risk_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=16, default="Low")
    status = models.CharField(max_length=32, default="Cleared")
    flag_reason = models.TextField(blank=True)


class WatchlistRule(ForensicBaseModel):
    rule_name = models.CharField(max_length=128)
    keyword = models.CharField(max_length=128)
    risk_weight = models.IntegerField(default=50)
    category = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
```
