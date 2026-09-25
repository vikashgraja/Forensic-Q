# `core` — Database Schema & ERD Specifications

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// ForensiQ Core Base Entity Model Schema
// dbdiagram.io specification
// ==========================================

Table forensic_base_model {
  id uuid [pk, note: 'UUID v4 Primary Key']
  created_at timestamp [default: `now()`, note: 'Ingestion timestamp']
  updated_at timestamp [default: `now()`, note: 'Last modification']
}

Table audit_sessions {
  id uuid [pk, default: `uuid4()`]
  session_token varchar(255) [not null, unique]
  is_authenticated boolean [default: false]
  ip_address varchar(45)
  user_agent varchar(255)
  created_at timestamp [default: `now()`]
  expires_at timestamp [not null]
}
```

---

## 2. Django Abstract ORM Models

```python
import uuid
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class ForensicBaseModel(UUIDModel, TimeStampedModel):
    class Meta:
        abstract = True
```
