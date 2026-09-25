# `q_scan` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
`q_scan` is the **Desktop Drive & File Triage Forensic Engine** of ForensiQ.
It provides:
1. **Endpoint Directory Scanning:** Recursive indexing of local/network drives, hidden files, and recent file access.
2. **Keyword & Regex Triage:** Rapid multi-threaded text search across PDFs, DOCX, XLSX, and TXT files.
3. **Evidence Artifact Mapping:** Pinpointing exact file locations, hashes (SHA-256), and access timestamps.

---

## 2. Strict Rules for Interns & Vibe-Coding
* Inherit all models from `core.models.ForensicBaseModel`.
* Use Tabulator grid with path truncating and file size formatters.
* Use `<c-base>`, `<c-stat_card>`, `<c-filter_bar>`, and `<c-data_grid>`.
