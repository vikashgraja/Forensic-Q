# `q_trail` — Database Schema & ERD Specifications

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// Q-Trail Money Trail & Fund Flow Schema
// dbdiagram.io specification
// ==========================================

Table cases {
  id uuid [pk, default: `uuid4()`]
  case_number varchar(64) [not null, unique]
  title varchar(255) [not null]
  lead_investigator varchar(128)
  status varchar(32) [default: 'Active']
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table fund_trail_paths {
  id uuid [pk, default: `uuid4()`]
  case_id uuid [ref: > cases.id]
  source_entity varchar(255) [not null]
  source_bank varchar(64) [not null]
  intermediate_hops json [note: 'Array of hop entities and timestamps']
  destination_entity varchar(255) [not null]
  destination_bank varchar(64) [not null]
  total_amount decimal(18,2) [not null]
  hop_count int [default: 1]
  is_circular boolean [default: false, note: 'True if funds return to originator']
  velocity_hours float [default: 0.0, note: 'Speed of pass-through in hours']
  risk_score int [default: 0]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]

  Note: 'Stitched multi-hop fund flow paths across banking institutions'
}

Table pass_through_nodes {
  id uuid [pk, default: `uuid4()`]
  trail_id uuid [ref: > fund_trail_paths.id]
  entity_name varchar(255) [not null]
  inflow_amount decimal(18,2) [not null]
  outflow_amount decimal(18,2) [not null]
  retention_pct float [default: 0.0, note: 'Percentage of funds retained']
  inflow_time timestamp [not null]
  outflow_time timestamp [not null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}
```

---

## 2. Django ORM Models

```python
from django.db import models
from core.models import ForensicBaseModel


class CaseDossier(ForensicBaseModel):
    case_number = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    lead_investigator = models.CharField(max_length=128)
    status = models.CharField(max_length=32, default="Active")


class FundTrailPath(ForensicBaseModel):
    case = models.ForeignKey(CaseDossier, on_delete=models.CASCADE, related_name="fund_trails")
    source_entity = models.CharField(max_length=255)
    source_bank = models.CharField(max_length=64)
    intermediate_hops = models.JSONField(default=list)
    destination_entity = models.CharField(max_length=255)
    destination_bank = models.CharField(max_length=64)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    hop_count = models.IntegerField(default=1)
    is_circular = models.BooleanField(default=False)
    velocity_hours = models.FloatField(default=0.0)
    risk_score = models.IntegerField(default=0)
```
