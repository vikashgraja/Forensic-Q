# `demo` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
The `demo` application provides reference implementations, interactive sandboxes, and production showcases for:
1. **Interactive Forensic Ledgers (`Tabulator.js`):** Client-side sorting, pagination, multi-column search, risk score progress bars, currency formatters, calculation footers, CSV/JSON export, and modal dossiers.
2. **Analytical Visualizers (`Plotly.py`):** Dark-mode bar charts, outflow distributions, and responsive visualization containers.
3. **Cotton Tag Usage Examples:** Real-world examples of `<c-base>`, `<c-page_header>`, `<c-stat_card>`, `<c-filter_bar>`, `<c-card>`, `<c-modal>`, `<c-data_grid>`, and `<c-chart>`.

---

## 2. Directory Structure
```
demo/
├── views.py                  # tabulator_demo_view, component_test_view
├── urls.py                   # /demo/tabulator/, /demo/sandbox/
├── templates/demo/
│   ├── tabulator_demo.html   # Forensic Transaction Ledger with Tabulator & Modals
│   └── test_dashboard.html   # Plotly charts + Tabulator grid visualizer
├── INSTRUCTION.md            # Developer guide (this file)
├── SCHEMA.md                 # Sample mock transaction & column specs
└── USER_GUIDE.md             # How to interact with the demo workstation
```

---

## 3. Strict Rules for Interns & Vibe-Coding

> [!IMPORTANT]
> **Rule 1: Dynamic Props Binding Syntax**
> When passing Python data into Cotton components, always use `:prop="val"` syntax:
> ```html
> <!-- CORRECT -->
> <c-chart title="Outflows" :figure_html="chart_html" />
> <c-data_grid id="grid" :columns="columns_json" :data="data_json" />
>
> <!-- INCORRECT (Causes HTML entity escaping & raw string bugs) -->
> <c-chart title="Outflows" figure_html="{{ chart_html }}" />
> ```

> [!IMPORTANT]
> **Rule 2: Avoid Illegal Windows Colon Tags**
> On Windows systems, never use `<c-slot:actions>`. Always use standard attribute syntax `<c-slot name="actions">`.

> [!IMPORTANT]
> **Rule 3: Executive Tone**
> Never use placeholder text like "Lorem Ipsum", "Demo Data", "Powered by Tabulator.js", or "Streamlit". Always use realistic forensic terminology (e.g. Counterparty, Inflow, Wire Transfer, SAR Filing, Risk Severity).

---

## 4. How to Add a New Demo View
1. Add a view function in `demo/views.py` returning JSON-serialized column/data dictionaries.
2. Add a template in `demo/templates/demo/<view_name>.html` wrapped in `<c-base>`.
3. Register the route in `demo/urls.py` (e.g. `path('my-demo/', views.my_demo_view, name='my_demo')`).
