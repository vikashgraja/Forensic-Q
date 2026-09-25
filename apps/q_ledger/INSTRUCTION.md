# `q_ledger` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
`q_ledger` is the **SAP & Corporate ERP Forensic Engine** of ForensiQ.
It provides:
1. **Three-Way Matching Auditing:** Comparing Purchase Orders (PO), Goods Receipt Notes (GRN), and Vendor Invoices for price inflation, quantity variance, or ghost deliveries.
2. **ERP Master Data Audit:** Detecting vendor bank account modifications immediately preceding large disbursements.
3. **Sequential & Split PO Detection:** Catching procurement threshold avoidance (smurfing purchase orders just below director approval limits).

---

## 2. Strict Rules for Interns & Vibe-Coding
* Inherit all models from `core.models.ForensicBaseModel`.
* Use `<c-base>`, `<c-stat_card>`, `<c-filter_bar>`, and `<c-data_grid>`.
