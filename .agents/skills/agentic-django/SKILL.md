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

---

## 3. Universal Logging Standards (Loguru)

All forensic modules, background threads, and parser engines must use Loguru:

```python
from loguru import logger

# Contextual structured logging
logger.info("Starting forensic ingestion for Case {} (Size: {} bytes)", audit_ref, file_size)
logger.warning("Unreadable block at offset {}: skipping gracefully", offset)
logger.error("Failed to parse evidence file: {}", err)
```

- **Interceptor Architecture:** `core.logging.setup_logging()` intercepts standard Python/Django logs and formats them via Loguru.
- **Log Sinks:** Colorized console output + rotating file logs (`logs/forensiq_{time:YYYY-MM-DD}.log` with 50MB rotation, 30 days retention, zip compression, and thread-safe queueing).
- **App Startup Hook:** Initialized in `core/apps.py` `ready()` method.

---

## 4. Large Evidence File Ingestion & Chunked Uploader (50+ GB)

For handling massive forensic datasets (PST archives, PCAPs, disk images, transaction logs) without timeouts or memory spikes:

1. **Browser Chunking:** Web UI splits files into 10–50 MB chunks using JavaScript `Blob.slice()` and uploads sequentially.
2. **Universal Uploader (`core.file_uploader.FileUploader`):**
   - Appends incoming binary chunks directly to physical disk (`media/uploads/...`).
   - Tracks sequence, resumes uploads, and stream-computes SHA-256 evidence chain-of-custody hashes on the fly.
3. **Background Asynchronous Worker:**
   - On completion of the last chunk, automatically spawns a daemon worker thread (`threading.Thread` or Celery task).
   - Updates progress percentage and current folder in the database for real-time frontend polling (`/api/progress/`).

---

## 5. Streaming Batch Ingestion & N+1 Prevention

When parsing large evidence sets into the database:

1. **Iterators & Streaming Parsers:** In `backend/`, stream records using Python generators (`yield`) instead of collecting everything in memory.
2. **Atomic Batch Inserts:** In `services.py`, accumulate messages in batches of 250 items and flush using `bulk_create()` wrapped in `@transaction.atomic`:

```python
@transaction.atomic
def _flush_message_batch(investigation, message_batch, attachment_map):
    created_messages = EmailMessage.objects.bulk_create(message_batch)
    attachment_objects = []
    for batch_idx, attachments in attachment_map:
        msg_instance = created_messages[batch_idx]
        for att in attachments:
            attachment_objects.append(EmailAttachment(email=msg_instance, ...))
    if attachment_objects:
        EmailAttachment.objects.bulk_create(attachment_objects)
```

---

## 6. Anti-Patterns & Prohibitions

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
6. **NO Bare Exception Pass or Continue (Bandit B110/B112):**
   - Never write `except Exception: pass` or `except Exception: continue`. Always catch `except Exception as e:` and log explicitly with `logger.debug(...)` or `logger.warning(...)`.
7. **NO Monolithic File Uploads for Files > 100MB:**
   - Always route large forensic evidence through `core.file_uploader.FileUploader`.
