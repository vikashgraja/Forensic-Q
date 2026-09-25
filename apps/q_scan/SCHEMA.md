# `q_scan` — Database Schema & ERD Specifications

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// Q-Scan Desktop Drive & File Forensics Schema
// dbdiagram.io specification
// ==========================================

Table scanned_devices {
  id uuid [pk, default: `uuid4()`]
  hostname varchar(128) [not null]
  drive_letter varchar(8) [not null]
  file_system varchar(32)
  total_files_scanned int [default: 0]
  scan_completed_at timestamp
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table file_evidence_hits {
  id uuid [pk, default: `uuid4()`]
  device_id uuid [ref: > scanned_devices.id]
  file_path varchar(1024) [not null]
  filename varchar(255) [not null]
  extension varchar(16)
  file_size_bytes bigint [not null]
  sha256_hash varchar(64) [not null]
  matched_keyword varchar(128) [not null]
  hit_count int [default: 1]
  snippet text [note: 'Context text snippet surrounding hit']
  created_time timestamp [not null]
  modified_time timestamp [not null]
  is_deleted boolean [default: false]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}
```

---

## 2. Django ORM Models

```python
from django.db import models
from core.models import ForensicBaseModel


class ScannedDevice(ForensicBaseModel):
    hostname = models.CharField(max_length=128)
    drive_letter = models.CharField(max_length=8)
    file_system = models.CharField(max_length=32, blank=True)
    total_files_scanned = models.IntegerField(default=0)
    scan_completed_at = models.DateTimeField(null=True, blank=True)


class FileEvidenceHit(ForensicBaseModel):
    device = models.ForeignKey(ScannedDevice, on_delete=models.CASCADE, related_name="hits")
    file_path = models.CharField(max_length=1024)
    filename = models.CharField(max_length=255)
    extension = models.CharField(max_length=16, blank=True)
    file_size_bytes = models.BigIntegerField()
    sha256_hash = models.CharField(max_length=64)
    matched_keyword = models.CharField(max_length=128)
    hit_count = models.IntegerField(default=1)
    snippet = models.TextField()
    created_time = models.DateTimeField()
    modified_time = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)
```
