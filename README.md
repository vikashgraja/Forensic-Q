# ForensiQ — Enterprise Forensic Intelligence Platform

ForensiQ is a modular forensic audit and corporate financial investigation system built with Django 5, Tailwind CSS, Django Cotton component architecture, Tabulator.js data grids, and Plotly analytics.

---

## 🏛️ Architecture & Application Modules

The system is organized into modular forensic engines and UI layers:

| Module / App | Description | Schema & ERD | User Guide | Instructions |
| :--- | :--- | :--- | :--- | :--- |
| **`core/`** | Master authentication, base models, dynamic engine discovery | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/core/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/core/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/core/INSTRUCTION.md) |
| **`ui/`** | Cotton design system tokens, components, and telemetry | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/ui/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/ui/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/ui/INSTRUCTION.md) |
| **`demo/`** | Reference UI implementation, Tabulator sandbox, and Plotly charts | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/demo/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/demo/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/demo/INSTRUCTION.md) |
| **`apps/q_bank/`** | Bank statement parsing, round-tripping, risk scoring | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_bank/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_bank/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_bank/INSTRUCTION.md) |
| **`apps/q_trail/`** | Multi-hop fund flow tracing, circular loop detection | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_trail/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_trail/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_trail/INSTRUCTION.md) |
| **`apps/q_mail/`** | PST/EML email parser, header analysis, attachment hashes | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_mail/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_mail/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_mail/INSTRUCTION.md) |
| **`apps/q_scan/`** | Endpoint and drive forensic scanner, keyword triage | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_scan/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_scan/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_scan/INSTRUCTION.md) |
| **`apps/q_verify/`** | Document metadata, PDF hex editing detection, EXIF analysis | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_verify/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_verify/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_verify/INSTRUCTION.md) |
| **`apps/q_link/`** | Cross-module entity resolution, fraud syndicate networks | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_link/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_link/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_link/INSTRUCTION.md) |
| **`apps/q_voice/`** | Audio wiretap/call transcription, speaker diarization | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_voice/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_voice/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_voice/INSTRUCTION.md) |
| **`apps/q_ledger/`** | SAP/ERP 3-way matching, phantom vendors, invoice variance | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_ledger/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_ledger/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_ledger/INSTRUCTION.md) |
| **`apps/q_chat/`** | Teams, Slack, WhatsApp chat thread reconstruction | [SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_chat/SCHEMA.md) | [USER_GUIDE.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_chat/USER_GUIDE.md) | [INSTRUCTION.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_chat/INSTRUCTION.md) |

---

## 📊 Database Schemas & Visual ERDs (dbdiagram.io)

All data models and relational tables across ForensiQ are documented in standard **DBML (Database Markup Language)** inside each app's `SCHEMA.md`.

### How to Visualize Diagrams:
1. Open any `SCHEMA.md` file (e.g. [apps/q_bank/SCHEMA.md](file:///d:/Vikash/Hyundai/Code/Forensic-Q/apps/q_bank/SCHEMA.md)).
2. Copy the code block under `## 1. DBML`.
3. Open **[https://dbdiagram.io](https://dbdiagram.io)** in your browser.
4. Paste the DBML into the editor on the left to instantly render visual Entity-Relationship diagrams, foreign key relationships, and field notes.

---

## 🔒 Pre-Commit Quality Hook & Rules Enforcement

To ensure code quality and strict adherence to documentation across intern vibe-coding workflows, a Git pre-commit hook is provided.

### 1. Manual Verification & Quality Check
Run the validator script at any time to verify documentation, linting, and Django integrity:
```bash
uv run python scripts/validate_project.py
```

### What the Validator Enforces:
1. **Mandatory Documentation:** Every app must have non-empty `INSTRUCTION.md`, `SCHEMA.md` (with DBML code blocks for dbdiagram.io), and `USER_GUIDE.md`.
2. **Cotton Template Standards:** Validates that no illegal `<c-slot:name>` tags are used (must use `<c-slot name="name">`).
3. **Django Sanity Checks:** Executes `python manage.py check` to guarantee zero syntax or ORM errors before any commit can succeed.

---

## 🚀 Getting Started

### 1. Run Development Server
```bash
uv run python manage.py runserver 127.0.0.1:8000
```

### 2. Access the Portal
- **Landing Dashboard:** `http://127.0.0.1:8000/`
- **Master Authentication Portal:** Enter master portal access password to unlock analytical engines.
