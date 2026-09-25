# `q_verify` — Database Schema & ERD Specifications

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// Q-Verify Document Authenticity Schema
// dbdiagram.io specification
// ==========================================

Table verified_documents {
  id uuid [pk, default: `uuid4()`]
  filename varchar(255) [not null]
  file_path varchar(1024) [not null]
  mime_type varchar(128) [not null]
  sha256_hash varchar(64) [not null]
  file_created_at timestamp [not null]
  file_modified_at timestamp [not null]
  meta_created_at timestamp [note: 'Embedded PDF/Office creation timestamp']
  meta_modified_at timestamp [note: 'Embedded PDF/Office modification timestamp']
  meta_author varchar(255)
  meta_software varchar(255) [note: 'e.g. Adobe Acrobat, Microsoft Word, Canva']
  has_timestamp_anomaly boolean [default: false]
  has_author_anomaly boolean [default: false]
  authenticity_score int [default: 100, note: '100 = Authentic, <50 = Suspect']
  anomaly_details json
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}
```

---

## 2. Django ORM Models

```python
from django.db import models
from core.models import ForensicBaseModel


class VerifiedDocument(ForensicBaseModel):
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=1024)
    mime_type = models.CharField(max_length=128)
    sha256_hash = models.CharField(max_length=64)
    file_created_at = models.DateTimeField()
    file_modified_at = models.DateTimeField()
    meta_created_at = models.DateTimeField(null=True, blank=True)
    meta_modified_at = models.DateTimeField(null=True, blank=True)
    meta_author = models.CharField(max_length=255, blank=True)
    meta_software = models.CharField(max_length=255, blank=True)
    has_timestamp_anomaly = models.BooleanField(default=False)
    has_author_anomaly = models.BooleanField(default=False)
    authenticity_score = models.IntegerField(default=100)
    anomaly_details = models.JSONField(default=dict)
```
