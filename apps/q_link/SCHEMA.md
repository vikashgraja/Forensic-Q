# `q_link` — Database Schema & ERD Specifications

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// Q-Link Entity Correlator Schema
// dbdiagram.io specification
// ==========================================

Table forensic_entities {
  id uuid [pk, default: `uuid4()`]
  entity_type varchar(32) [note: 'Individual, Company, BankAccount, Email, Device']
  identifier varchar(255) [not null, unique]
  display_name varchar(255) [not null]
  risk_rating int [default: 0]
  is_target boolean [default: false]
  metadata json
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table entity_relationships {
  id uuid [pk, default: `uuid4()`]
  source_entity_id uuid [ref: > forensic_entities.id]
  target_entity_id uuid [ref: > forensic_entities.id]
  relation_type varchar(64) [note: 'DirectorOf, TransferredFunds, SharedAddress, Emailed']
  confidence_score float [default: 1.0]
  source_module varchar(32) [note: 'q_bank, q_mail, q_verify, q_voice, q_ledger']
  evidence_ref varchar(255)
  weight float [default: 1.0]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}
```

---

## 2. Django ORM Models

```python
from django.db import models
from core.models import ForensicBaseModel


class ForensicEntity(ForensicBaseModel):
    entity_type = models.CharField(max_length=32)
    identifier = models.CharField(max_length=255, unique=True, db_index=True)
    display_name = models.CharField(max_length=255)
    risk_rating = models.IntegerField(default=0)
    is_target = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)


class EntityRelationship(ForensicBaseModel):
    source_entity = models.ForeignKey(
        ForensicEntity, on_delete=models.CASCADE, related_name="out_relations"
    )
    target_entity = models.ForeignKey(
        ForensicEntity, on_delete=models.CASCADE, related_name="in_relations"
    )
    relation_type = models.CharField(max_length=64)
    confidence_score = models.FloatField(default=1.0)
    source_module = models.CharField(max_length=32)
    evidence_ref = models.CharField(max_length=255, blank=True)
    weight = models.FloatField(default=1.0)
```
