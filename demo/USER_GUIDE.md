# `demo` — User & Operations Guide

## 1. Forensic Transaction Ledger (`/demo/tabulator/`)

The Forensic Transaction Ledger provides a high-density audit workbench:

### 1.1 Multi-Criteria Filtering
* **Global Search:** Type keywords, entity names, reference numbers, or account masks in the live search bar.
* **Direction Filter:** Filter by `All Directions`, `IN (Credits)`, or `OUT (Debits)`.
* **Risk Severity Filter:** Scrutinize `High Risk (>75)`, `Medium Risk (35-75)`, or `Low Risk (<35)`.
* **Investigation Status:** Filter by `Escalated`, `Flagged`, `Under Review`, or `Cleared`.
* **Reset Filters:** Click the **Reset Filters** button to restore the full transaction dataset.

### 1.2 Inspecting Transaction Details (Dossier Modal)
* Click any transaction row in the table to open its **Transaction Forensic Dossier**.
* Inspect the full counterparty details, masked account, transfer value, and detailed forensic flag reasoning.
* Click **Add to Case Dossier** to flag the item for case reporting.

### 1.3 Exporting Audit Reports
* **Export CSV:** Downloads the filtered table data as `forensic_transactions_report.csv`.
* **Export JSON:** Generates a structured JSON payload for external intelligence ingest.
* **Print Dossier:** Opens a print-optimized layout of the currently filtered ledger.

---

## 2. Analytics Visualizer (`/demo/sandbox/`)
* Displays vendor outflow distributions and high-risk counterparty allocations via interactive charts.
* Hover over chart bars to view precise transfer amounts and transaction volumes.
