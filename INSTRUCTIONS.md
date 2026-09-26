# ForensiQ — Developer Instructions & Architecture Guide

## 1. Project Overview & Vision

**ForensiQ** is a modern, high-performance forensic investigation and analytical workstation built on **Django 6.1**, **django-cotton**, **Tabulator.js**, and **Plotly.py**.

Key platform capabilities:
- **Instant Client-Side Interactivity:** Tabulator.js handles sorting, pagination, column reordering, multi-field filtering, and CSV/JSON export on the client side without unnecessary server roundtrips.
- **Franken UI / Dark Mode Aesthetic:** Deep Zinc-950 dark mode with an interactive Sun/Moon theme switcher and persistent `localStorage` theme state.
- **Component-Driven HTML-First Architecture:** Clean, modular Django Cotton custom tags (`<c-base>`, `<c-stat_card>`, `<c-filter_bar>`, `<c-data_grid>`, `<c-chart>`).
- **Production-Ready Python Backend:** Powered by Django's ORM, authentication, routing, and analytical data pipelines.

---

## 2. Directory Architecture

```
Forensic-Q/
├── ForensiQ/                   # Django project configuration
│   ├── settings.py            # Global settings & apps sys.path setup
│   ├── urls.py                # Top-level URL routing
│   ├── asgi.py / wsgi.py
├── apps/                      # Modular Forensic Analytical Engines
│   ├── q_bank/                # Financial & bank statement ledger analysis
│   ├── q_chat/                # Communication log & chat forensics
│   └── q_link/                # Entity link & network graph analysis
├── core/                      # Core base models (ForensicBaseModel, TimeStampedModel) & utilities
│   ├── models.py
│   └── apps.py
├── demo/                      # Component sandbox & Tabulator demo
│   ├── views.py
│   ├── urls.py
│   ├── apps.py
│   └── templates/demo/        # Demo dashboard templates
│       ├── tabulator_demo.html# Forensic transaction ledger demo
│       └── test_dashboard.html# Component test sandbox
├── ui/                        # Centralized UI Design System
│   ├── STYLE_GUIDE.md         # UI Style Guide & Cotton Component Catalog
│   ├── apps.py
│   └── templates/cotton/      # ALL REUSABLE COTTON COMPONENTS
│       ├── base.html          # Root shell, dark theme & theme switcher
│       ├── page_header.html   # Breadcrumb, title, and action toolbar
│       ├── stat_card.html     # KPI metric widgets (sky, emerald, amber, rose)
│       ├── card.html          # Standard card containers
│       ├── filter_bar.html    # Multi-column instant filter toolbar
│       ├── badge.html         # Status & risk badges
│       ├── modal.html         # Forensic detail dossiers
│       ├── data_grid.html     # Tabulator.js data tables
│       ├── chart.html         # Plotly visualization containers
│       └── module_card.html   # 6-engine forensic module card component
├── manage.py
├── pyproject.toml             # uv package dependencies
└── INSTRUCTIONS.md            # Developer instructions (this file)
```

---

## 3. Technology Stack

* **Runtime:** Python `>=3.13` managed with [`uv`](https://docs.astral.sh/uv/)
* **Web Framework:** Django `6.1.1`
* **Component Engine:** [`django-cotton`](https://django-cotton.com/) (`>=2.7.2`)
* **Interactive Data Grid:** [Tabulator.js](https://tabulator.info/) `v6.3.0`
* **Visualization:** `plotly` (`>=7.1.0`) + Plotly.js (`plotly_dark` theme)
* **Design & Styling:** Tailwind CSS (`dark:` mode class), FontAwesome 6, Google Fonts (Inter, JetBrains Mono)

---

## 4. Running the Workstation

Always execute commands with `uv run`:
```bash
# Apply database migrations
uv run python manage.py migrate

# Check for system configuration issues
uv run python manage.py check

# Run local development server
uv run python manage.py runserver 127.0.0.1:8000
```

### Endpoints & Access
* **Portal Login:** [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/) *(Configured via `PORTAL_ACCESS_PASSWORD` in `.env`)*
* **Q-Mail Investigation Hub:** [http://127.0.0.1:8000/mail/](http://127.0.0.1:8000/mail/)
* **Demo Forensic Ledger:** [http://127.0.0.1:8000/demo/tabulator/](http://127.0.0.1:8000/demo/tabulator/)
* **Demo Component Sandbox:** [http://127.0.0.1:8000/demo/sandbox/](http://127.0.0.1:8000/demo/sandbox/)
* **Django Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 5. Building Forensic Dashboards with Cotton

Building a new dashboard page is simple and clean:

```html
<c-base title="Forensic Report">

    <!-- 1. Page Header with Action Buttons -->
    <c-page_header title="Entity Flow Ledger" subtitle="Interactive audit" icon="fa-solid fa-network-wired">
        <button id="btn-export" class="px-3 py-1.5 bg-amber-500 text-zinc-950 font-bold rounded-lg text-xs">
            Export CSV
        </button>
    </c-page_header>

    <!-- 2. KPI Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <c-stat_card title="Volume" value="₹14.2M" variant="emerald" icon="fa-solid fa-arrow-trend-up" />
        <c-stat_card title="Flagged" value="12" variant="rose" icon="fa-solid fa-triangle-exclamation" />
        <c-stat_card title="Entities" value="84" variant="sky" icon="fa-solid fa-users" />
    </div>

    <!-- 3. Visuals & Data Table -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <c-chart title="Outflow Distribution" :figure_html="chart_html" />
        <c-data_grid id="entity-grid" title="Entity Registry" :columns="columns_json" :data="data_json" />
    </div>

</c-base>
```

---

## 6. Critical Template & Cotton Rules

1. **Root Layout Component:** Use `<c-base title="...">` to wrap all dashboard pages.
2. **Dynamic Props Binding:** Always use `:prop="variable"` for dynamic Django variables (e.g. `:figure_html="chart_html"` or `:data="table_data"`).
3. **Named Slots Syntax:** Always use `<c-slot name="...">` (e.g. `<c-slot name="actions">`).
4. **No `<c-` tags in HTML Comments:** Use `{% comment %}...{% endcomment %}` to avoid unclosed tag parse errors.

---

## 7. Dynamic Forensic Engine Registry (`apps/`)

All analytical modules placed in `apps/` are automatically discovered and rendered as interactive cards on the workstation landing page.

To configure an app's display card, define metadata attributes in its `AppConfig` (`apps/<app_name>/apps.py`):

```python
from django.apps import AppConfig


class QBankConfig(AppConfig):
    name = "q_bank"
    verbose_name = "Q-Bank"

    # Forensic Landing Page Card Metadata
    module_num = "01"
    module_category = "MONEY"
    module_name = "Bank"
    module_tag = "LIVE"
    module_accent = "orange"  # orange, gold, purple, teal, rose, amber
    module_tagline = "Reads statements. Flags keywords."
    module_features = [
        "Flagged transactions, vendor & party summary",
        "Tuneable watchlist per investigation",
    ]
    module_url = "/demo/tabulator/"
    module_order = 1
```

*Grid Layout Rule:* If the total number of apps is not a multiple of 3, the final row automatically centers cards across the workstation grid.

