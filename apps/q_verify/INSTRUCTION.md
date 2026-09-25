# `q_verify` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
`q_verify` is the **Document Authenticity & Metadata Forensic Engine** of ForensiQ.
It provides:
1. **Metadata Discrepancy Auditing:** Compares internal PDF/Office document creation timestamps vs file system timestamps to catch post-facto edits.
2. **Author & Software Inspection:** Extracts embedded author tags, software generators (e.g. Photoshop, PDF editors), and editing history.
3. **Integrity Scoring:** Calculates authenticity risk scores for invoices, contracts, and board minutes.

---

## 2. Strict Rules for Interns & Vibe-Coding
* Inherit all models from `core.models.ForensicBaseModel`.
* Highlight discrepancies with `<c-badge>` variants (`rose` for modified, `emerald` for authentic).
* Use `<c-base>`, `<c-stat_card>`, `<c-filter_bar>`, and `<c-data_grid>`.
