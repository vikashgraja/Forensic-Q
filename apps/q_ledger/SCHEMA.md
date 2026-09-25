# `q_ledger` — Database Schema & ERD Specifications

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// Q-Ledger ERP & Procurement Forensics Schema
// dbdiagram.io specification
// ==========================================

Table vendors {
  id uuid [pk, default: `uuid4()`]
  vendor_code varchar(64) [not null, unique]
  vendor_name varchar(255) [not null]
  gstin varchar(32)
  bank_account_no varchar(64)
  ifsc_code varchar(32)
  is_flagged boolean [default: false]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table purchase_orders {
  id uuid [pk, default: `uuid4()`]
  po_number varchar(64) [not null, unique]
  vendor_id uuid [ref: > vendors.id]
  po_date timestamp [not null]
  total_amount decimal(18,2) [not null]
  approved_by varchar(128)
  is_split_po boolean [default: false]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table erp_three_way_matches {
  id uuid [pk, default: `uuid4()`]
  po_id uuid [ref: > purchase_orders.id]
  invoice_number varchar(64) [not null]
  grn_number varchar(64) [not null]
  po_amount decimal(18,2) [not null]
  grn_amount decimal(18,2) [not null]
  invoice_amount decimal(18,2) [not null]
  variance_amount decimal(18,2) [default: 0.00]
  has_anomaly boolean [default: false]
  anomaly_type varchar(64) [note: 'Ghost Delivery, Price Inflation, Quantity Discrepancy']
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}
```

---

## 2. Django ORM Models

```python
from django.db import models
from core.models import ForensicBaseModel


class VendorMaster(ForensicBaseModel):
    vendor_code = models.CharField(max_length=64, unique=True, db_index=True)
    vendor_name = models.CharField(max_length=255)
    gstin = models.CharField(max_length=32, blank=True)
    bank_account_no = models.CharField(max_length=64, blank=True)
    ifsc_code = models.CharField(max_length=32, blank=True)
    is_flagged = models.BooleanField(default=False)


class PurchaseOrder(ForensicBaseModel):
    po_number = models.CharField(max_length=64, unique=True, db_index=True)
    vendor = models.ForeignKey(VendorMaster, on_delete=models.CASCADE, related_name="orders")
    po_date = models.DateTimeField(db_index=True)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    approved_by = models.CharField(max_length=128)
    is_split_po = models.BooleanField(default=False)


class ERPThreeWayMatch(ForensicBaseModel):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="matches")
    invoice_number = models.CharField(max_length=64)
    grn_number = models.CharField(max_length=64)
    po_amount = models.DecimalField(max_digits=18, decimal_places=2)
    grn_amount = models.DecimalField(max_digits=18, decimal_places=2)
    invoice_amount = models.DecimalField(max_digits=18, decimal_places=2)
    variance_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.0)
    has_anomaly = models.BooleanField(default=False)
    anomaly_type = models.CharField(max_length=64, blank=True)
```
