# `ui` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
The `ui` application contains the standardized **ForensiQ Design System** and **Django Cotton Component Suite** (`ui/templates/cotton/`).

All dashboard views across all analytical modules (`q_bank`, `q_mail`, `q_trail`, etc.) MUST use the reusable Cotton components in `ui/templates/cotton/` to guarantee visual consistency.

---

## 2. Directory Structure
```
ui/
├── STYLE_GUIDE.md            # Comprehensive color token & typography manual
├── INSTRUCTION.md            # Developer guide (this file)
├── SCHEMA.md                 # Component prop signatures & slot specifications
├── USER_GUIDE.md             # How to build pages using Cotton tags
└── templates/cotton/         # ALL REUSABLE COTTON COMPONENTS
    ├── base.html             # Root shell with dark mode & header
    ├── page_header.html      # Breadcrumb, title, and action toolbar
    ├── stat_card.html        # KPI metric widgets (sky, emerald, amber, rose, slate)
    ├── card.html             # Standard card containers
    ├── filter_bar.html       # Multi-column instant filter toolbar
    ├── badge.html            # Status & risk badges
    ├── modal.html            # Forensic detail dossiers
    ├── data_grid.html        # Tabulator.js data tables
    ├── chart.html            # Plotly visualization containers
    └── module_card.html      # Forensic engine landing card
```

---

## 3. Strict Rules for Interns & Vibe-Coding

> [!CRITICAL]
> **Rule 1: Always Register Reusable UI in `ui/templates/cotton/`**
> Never write custom container styles or one-off table wrappers in individual apps. All reusable components must live in `ui/templates/cotton/`.

> [!CRITICAL]
> **Rule 2: Never Use Windows Colon Syntax**
> Use `<c-slot name="actions">`. Never use `<c-slot:actions>` (triggers `[WinError 123]` on Windows systems).

> [!CRITICAL]
> **Rule 3: Use Tokenized Colors Only**
> Use curated tokens:
> * Dark Background: `dark:bg-zinc-950` (`#09090b`)
> * Card Surface: `dark:bg-zinc-900` (`#18181b`)
> * Border: `dark:border-zinc-800` (`#27272a`)
> * Brand Accent: `text-amber-500` / `bg-amber-500` (`#f59e0b`)
