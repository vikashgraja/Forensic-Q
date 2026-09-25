# ForensiQ UI Style Guide & Component Catalog
## Modern Forensic Analytics Workstation with Dark Mode

This document establishes the official design system, color tokens, dark mode implementation, and Cotton component library for **ForensiQ**.

---

## 1. Aesthetic Vision: Franken UI / Dark Theme Aesthetic

ForensiQ implements a **modern dark design system** tailored for high-density forensic analytics:
* **Canvas:** Deep Zinc-950 (`#09090b` / `dark:bg-zinc-950`)
* **Surfaces & Cards:** Zinc-900 (`#18181b` / `dark:bg-zinc-900`) with crisp `border-zinc-800` (`#27272a`) borders.
* **Header Bar:** Translucent `bg-zinc-950/80` with backdrop blur (`backdrop-blur-md`).
* **Accents & Highlights:** Warm Amber (`#f59e0b` / `amber-500`) as the primary brand accent, with Sky-400 for info, Emerald-400 for credits/low risk, and Rose-500 for alerts/outflows.
* **Theme Switching:** Instant dark/light mode toggle with zero page flicker (FOUC-prevented inline script) and `localStorage` persistence.

---

## 2. Color Palette & Dark Mode Tokens

| Surface / Element | Light Mode Class | Dark Mode Class | Hex Code |
| :--- | :--- | :--- | :--- |
| **Canvas Background** | `bg-slate-50` | `dark:bg-zinc-950` | `#09090b` |
| **Card Surface** | `bg-white` | `dark:bg-zinc-900` | `#18181b` |
| **Borders & Dividers** | `border-slate-200` | `dark:border-zinc-800` | `#27272a` |
| **Primary Text** | `text-slate-900` | `dark:text-zinc-100` / `text-white` | `#f4f4f5` / `#ffffff` |
| **Muted / Subtitle Text** | `text-slate-500` | `dark:text-zinc-400` | `#a1a1aa` |
| **Brand Accent (Amber)** | `bg-amber-500` | `bg-amber-500` / `text-amber-400` | `#f59e0b` |
| **Positive / Credit (Emerald)**| `bg-emerald-50` | `dark:bg-emerald-950/50` | `#10b981` |
| **Alert / Flag (Rose)** | `bg-rose-50` | `dark:bg-rose-950/50` | `#f43f5e` |
| **Information / Links (Sky)** | `bg-sky-50` | `dark:bg-sky-950/50` | `#38bdf8` |

---

## 3. Typography Standards

* **Primary Font:** [Inter](https://fonts.google.com/specimen/Inter) (`font-sans`)
* **Monospace Font:** [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) (`font-mono`)
  * **MUST** be used for:
    * Reference & Transaction IDs (`TXN-98412`)
    * Bank Account Masks (`HDFC-****-8841`)
    * Monetary Figures (`+₹1,820,000`)
    * Timestamps (`2026-03-01 09:23`)

---

## 4. Cotton Component Catalog (`ui/templates/cotton/`)

### 4.1 Shell Layout with Theme Switcher — `<c-base>`
```html
<c-base title="ForensiQ | Forensic Ledger">
    <!-- Content injected here -->
</c-base>
```

### 4.2 Page Header — `<c-page_header>`
```html
<c-page_header 
    title="Forensic Transaction Ledger" 
    subtitle="Interactive financial audit log."
    icon="fa-solid fa-money-bill-transfer"
    icon_color="text-amber-500"
    category="Q-Bank Analytics"
    section="Forensic Engine">

    <!-- Action Slot -->
    <button class="px-3.5 py-2 rounded-lg bg-zinc-900 dark:bg-amber-500 text-white dark:text-zinc-950 text-xs font-bold shadow-sm">
        <i class="fa-solid fa-file-csv mr-1"></i> Export Report
    </button>
</c-page_header>
```

### 4.3 KPI Metric Card — `<c-stat_card>`
```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <c-stat_card 
        title="Total Inflow" 
        value="₹12,450,000" 
        subtitle="14 verified credits" 
        icon="fa-solid fa-arrow-down-left" 
        variant="emerald" />

    <c-stat_card 
        title="High Risk Alerts" 
        value="6" 
        extra="(3 Escalated)"
        subtitle="Requires immediate review" 
        icon="fa-solid fa-triangle-exclamation" 
        variant="rose" />
</div>
```

### 4.4 Filter Toolbar — `<c-filter_bar>`
```html
<c-filter_bar cols="4">
    <!-- Filter inputs -->
    <div>
        <label class="block text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1">Search</label>
        <input type="text" id="search" placeholder="Search..." 
            class="w-full text-xs rounded-lg border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 text-slate-900 dark:text-zinc-100 p-2">
    </div>

    <c-slot name="summary">
        <span class="font-medium text-slate-700 dark:text-zinc-300 bg-slate-100 dark:bg-zinc-800 px-2.5 py-1 rounded text-xs">12 records selected</span>
    </c-slot>

    <c-slot name="actions">
        <button id="btn-reset" class="text-xs text-sky-600 dark:text-sky-400 hover:text-sky-800 font-semibold">Reset Filters</button>
    </c-slot>
</c-filter_bar>
```

### 4.5 Card Container — `<c-card>`
```html
<c-card title="Suspect Entity Profile" subtitle="Account #CANR-****-1002" icon="fa-solid fa-user-shield" icon_color="text-amber-500">
    <c-slot name="actions">
        <span class="text-xs bg-slate-100 dark:bg-zinc-800 px-2 py-1 rounded-full font-mono">Status: Flagged</span>
    </c-slot>

    <p class="text-sm text-slate-700 dark:text-zinc-300">Entity exhibits circular routing patterns across multiple shell accounts.</p>

    <c-slot name="footer">
        <span class="text-xs text-slate-400 dark:text-zinc-500">Last updated: 10 mins ago</span>
    </c-slot>
</c-card>
```

### 4.6 Status & Risk Badge — `<c-badge>`
```html
<c-badge text="Escalated" variant="rose" icon="fa-solid fa-triangle-exclamation" />
<c-badge text="Verified" variant="emerald" icon="fa-solid fa-check" />
<c-badge text="In Review" variant="sky" icon="fa-solid fa-hourglass-half" />
```

### 4.7 Forensic Detail Modal — `<c-modal>`
```html
<c-modal id="entity-modal" title="Entity Dossier" subtitle="Forensic Details" icon="fa-solid fa-shield-halved">
    <div class="space-y-3 text-sm">
        <p>Entity details and investigation notes go here.</p>
    </div>

    <c-slot name="footer">
        <button type="button" data-modal-close="entity-modal" class="px-4 py-2 text-xs bg-slate-100 dark:bg-zinc-800 dark:text-zinc-300 rounded-lg">Close</button>
        <button type="button" class="px-4 py-2 text-xs bg-zinc-900 dark:bg-amber-500 text-white dark:text-zinc-950 font-bold rounded-lg">Save Dossier</button>
    </c-slot>
</c-modal>
```

### 4.8 Plotly Chart Container — `<c-chart>`
```html
<c-chart title="Vendor Outflow Distribution" subtitle="Monthly aggregated debits" :figure_html="chart_html" />
```

### 4.9 Tabulator Data Grid — `<c-data_grid>`
```html
<c-data_grid 
    id="transactions-table" 
    title="Flagged Transactions" 
    subtitle="Filtered by risk threshold"
    :columns="table_columns" 
    :data="table_data" 
    pagination_size="10" />
```

### 4.10 Forensic Module Engine Card — `<c-module_card>`
Used on landing pages and workstation engine selectors:
```html
<c-module_card 
    num="01" 
    category="MONEY" 
    name="Bank" 
    tag="LIVE" 
    accent="orange" 
    href="/demo/tabulator/" 
    tagline="Reads statements. Flags keywords.">
    <p><span class="text-[#e87a4d] dark:text-[#f08a5d] font-bold">→</span> Flagged transactions, vendor &amp; party summary,</p>
    <p><span class="text-[#e87a4d] dark:text-[#f08a5d] font-bold">→</span> Tuneable watchlist per investigation.</p>
</c-module_card>
```
*Accents available:* `orange`, `gold`, `purple`, `teal`, `rose`, `amber`.

---

## 5. Tabulator.js Dark Mode Configuration

Tabulator is styled automatically to match the dark theme via CSS in `base.html`.

For custom formatters:
```javascript
// Example: Direction Pill Formatter
const directionFormatter = function(cell) {
    const val = cell.getValue();
    if (val === "IN") {
        return `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300"><i class="fa-solid fa-arrow-down mr-1"></i>IN</span>`;
    } else {
        return `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300"><i class="fa-solid fa-arrow-up mr-1"></i>OUT</span>`;
    }
};
```

---

## 6. Plotly.js Dark Theme Setup

In `views.py`, configure Plotly figures with transparent background and dark theme font colors:

```python
fig.update_layout(
    template="plotly_dark",
    margin=dict(l=20, r=20, t=30, b=20),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#a1a1aa"),
    xaxis=dict(gridcolor="#27272a", linecolor="#27272a"),
    yaxis=dict(gridcolor="#27272a", linecolor="#27272a"),
)
```

---

## 7. Django Cotton Rules & Gotchas

1. **Root Layout Component:** Always wrap templates with `<c-base title="...">`.
2. **Dynamic Props Binding:** Always use `:prop="variable"` for context variables (`:figure_html="chart_html"`, `:columns="table_columns"`, `:data="table_data"`).
3. **Named Slots Syntax:** Always use `<c-slot name="...">` (e.g. `<c-slot name="actions">`).
4. **No `<c-` tags in HTML comments:** Use `{% comment %}...{% endcomment %}`.
