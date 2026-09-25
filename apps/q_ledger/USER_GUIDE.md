# `q_ledger` — Investigator & Auditor User Guide

## 1. Investigative Workflow
1. **ERP Dump Ingestion:** Ingest SAP / Oracle / Tally procurement tables (PO, GRN, MIRO/Invoice).
2. **Execute Three-Way Match Engine:** Identify high variance payouts where payments exceeded goods physically received.
3. **Filter Ghost Deliveries:** Flag instances where invoices were paid without a matching warehouse GRN entry.
4. **Export Procurement Dossier:** Export tabular evidence dossiers summarizing procurement fraud and vendor collusion.
