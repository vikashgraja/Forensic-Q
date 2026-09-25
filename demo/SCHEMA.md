# `demo` — Database Schema & ERD Specifications

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// ForensiQ Demo Mock Records Schema
// dbdiagram.io specification
// ==========================================

Table mock_forensic_transactions {
  id int [pk, increment]
  ref_no varchar(64) [not null]
  txn_date timestamp [not null]
  party varchar(255) [not null]
  account_no varchar(64)
  category varchar(128)
  direction varchar(8) [note: 'IN / OUT']
  amount decimal(18,2) [not null]
  risk_score int [default: 0]
  risk_level varchar(16) [default: 'Low']
  status varchar(32) [default: 'Cleared']
  flag_reason text
}
```

---

## 2. Tabulator.js Columns Definition

```javascript
[
  { formatter: "rowSelection", width: 45, hozAlign: "center" },
  { title: "Ref No", field: "ref_no", width: 120 },
  { title: "Timestamp", field: "date", width: 140 },
  { title: "Counterparty Entity", field: "party", minWidth: 200 },
  { title: "Category", field: "category", width: 160 },
  { title: "Dir", field: "direction", width: 80, hozAlign: "center" },
  { title: "Amount (INR)", field: "amount", width: 140, hozAlign: "right", bottomCalc: "sum" },
  { title: "Risk Score", field: "risk_score", width: 130 },
  { title: "Status", field: "status", width: 130, hozAlign: "center" }
]
```
