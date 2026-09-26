---
name: agentic-django
description: >-
  Production-grade Django & Cotton architecture guidelines for AI coding assistants and developers.
  Enforces services/selectors separation, proactive N+1 elimination, atomic transactions, thin views,
  and clean Cotton component integration.
---

# Agentic Django Architecture & Vibe-Coding Standards

This skill encodes production-grade Django architecture patterns, preventing common AI failure modes like fat views, unoptimized N+1 queries, business logic in models/serializers, and spaghetti `post_save` signals.

---

## 1. Core Architectural Layout (Services & Selectors Pattern)

Every forensic analytical app (`apps/q_*`) must separate reads, writes, and presentation into dedicated layers:

```
apps/q_example/
├── backend/         # Dedicated forensic analysis scripts, parsers, algorithms
│   └── __init__.py
├── models.py        # Declarative schema (Matches SCHEMA.md & dbdiagram.io)
├── selectors.py     # Read-only queries (Proactive select_related / prefetch_related)
├── services.py      # Business logic & mutations (Pure functions, @transaction.atomic)
├── views.py         # Thin UI controllers (Parse inputs, invoke services/selectors)
├── urls.py          # App URL routing
├── INSTRUCTION.md   # App-specific dev requirements
├── SCHEMA.md        # dbdiagram.io DBML specification
└── USER_GUIDE.md    # Investigator workflow guide
```

---

## 2. Layer-by-Layer Rules

### 1. `models.py` — Clean, Declarative Schema
- Models inherit from `core.models.ForensicBaseModel` (provides `id` UUID v4, `created_at`, `updated_at`).
- **Rule:** Do NOT put complex business workflows or external API calls in model `save()` methods.
- **Rule:** Every model MUST implement `__str__()`.
- **Rule:** Use `models.CharField(max_length=..., blank=True, default="")` instead of `null=True` on text fields (Ruff `DJ001`).

```python
# apps/q_bank/models.py
from django.db import models
from core.models import ForensicBaseModel


class BankTransaction(ForensicBaseModel):
    account = models.ForeignKey(
        "BankAccount", on_delete=models.CASCADE, related_name="transactions"
    )
    txn_ref = models.CharField(max_length=128, unique=True)
    txn_date = models.DateTimeField(db_index=True)
    party_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    risk_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=16, default="Low")
    status = models.CharField(max_length=32, default="Cleared")

    def __str__(self):
        return f"{self.txn_ref} | {self.party_name} | {self.amount}"
```

---

### 2. `selectors.py` — Read-Only Queries & N+1 Elimination
- **Rule:** All queries used by views, Tabulator data grids, and Plotly charts MUST live in `selectors.py`.
- **Rule:** Always use `select_related()` for single-object relations (`ForeignKey`, `OneToOne`) and `prefetch_related()` for `ManyToManyField`.
- **Rule:** Functions in `selectors.py` MUST NEVER write or mutate database state.

```python
# apps/q_bank/selectors.py
from django.db.models import QuerySet
from .models import BankTransaction


def get_flagged_transactions(*, min_risk_score: int = 50) -> QuerySet[BankTransaction]:
    """
    Fetches high-risk transactions with joined account details to eliminate N+1 queries.
    """
    return (
        BankTransaction.objects.select_related("account")
        .filter(risk_score__gte=min_risk_score)
        .order_by("-risk_score", "-txn_date")
    )
```

---

### 3. `services.py` — Business Logic & Atomic Mutations
- **Rule:** All database writes, file parsers, scoring calculations, and state mutations live in `services.py`.
- **Rule:** Multi-table operations MUST be decorated with `@transaction.atomic`.
- **Rule:** External calls or background tasks MUST use `transaction.on_commit()`.

```python
# apps/q_bank/services.py
from decimal import Decimal
from django.db import transaction
from .models import BankAccount, BankTransaction


@transaction.atomic
def ingest_bank_statement_record(
    *, account: BankAccount, txn_ref: str, party_name: str, amount: Decimal, risk_score: int = 0
) -> BankTransaction:
    """
    Creates or updates a forensic transaction and triggers risk classification atomically.
    """
    risk_level = "High" if risk_score >= 70 else ("Medium" if risk_score >= 40 else "Low")

    txn, created = BankTransaction.objects.update_or_create(
        txn_ref=txn_ref,
        defaults={
            "account": account,
            "party_name": party_name,
            "amount": amount,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "status": "Flagged" if risk_score >= 70 else "Cleared",
        },
    )
    return txn
```

---

### 4. `views.py` — Thin Presentation Controllers
- **Rule:** Views must only handle HTTP routing, request parsing, authentication checks, and calling `selectors`/`services`.
- **Rule:** Never execute raw ORM filtering loops or math calculations inside `views.py`.

```python
# apps/q_bank/views.py
from django.shortcuts import render
from .selectors import get_flagged_transactions


def transactions_dashboard_view(request):
    min_score = int(request.GET.get("min_risk", 50))
    transactions = get_flagged_transactions(min_risk_score=min_score)

    # Prepare serializable data for Tabulator.js grid
    table_data = [
        {
            "id": str(t.id),
            "ref_no": t.txn_ref,
            "date": t.txn_date.strftime("%Y-%m-%d %H:%M"),
            "party": t.party_name,
            "amount": float(t.amount),
            "risk_score": t.risk_score,
            "risk_level": t.risk_level,
            "status": t.status,
        }
        for t in transactions
    ]

    return render(
        request,
        "q_bank/dashboard.html",
        {
            "table_data": table_data,
            "flagged_count": len(table_data),
        },
    )
```

---

## 3. Anti-Patterns & Prohibitions

1. **NO Business Logic in `post_save` Signals:**
   - Avoid `post_save` signals for triggering business workflows. Use explicit function calls in `services.py`.
2. **NO Unindexed Foreign Keys or Missing Select Related:**
   - Always verify foreign keys are indexed and queried with `select_related`.
3. **NO Direct Mutation in Selectors:**
   - Selectors are strictly read-only (`QuerySet` returning).
4. **NO `<c-slot:name>` Colon Syntax in Cotton Templates:**
   - Always use `<c-slot name="name">` to guarantee Windows filesystem compatibility.
5. **NO Uncommitted Model Changes:**
   - Always run `uv run python manage.py makemigrations` after changing `models.py`.
