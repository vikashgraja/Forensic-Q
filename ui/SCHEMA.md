# `ui` — UI Design System, Component Props & State Schema

> [!TIP]
> **dbdiagram.io Compatibility:** Copy and paste the DBML code below directly into [dbdiagram.io](https://dbdiagram.io) to generate visual Entity-Relationship diagrams for UI workspace preferences and telemetry state.

---

## 1. DBML (Database Markup Language for dbdiagram.io)

```dbml
// ==========================================
// ForensiQ UI Preferences & Component State Schema
// dbdiagram.io specification
// ==========================================

Table user_ui_preferences {
  id uuid [pk, default: `uuid4()`]
  user_identifier varchar(128) [not null, unique, note: 'Session hash or user tag']
  theme varchar(32) [default: 'dark', note: 'dark, light, high-contrast']
  grid_page_size int [default: 25]
  default_accent_color varchar(32) [default: 'orange']
  enable_animations boolean [default: true]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]

  Note: 'Stores user-specific UI layout preferences and dashboard configurations'
}

Table grid_saved_layouts {
  id uuid [pk, default: `uuid4()`]
  user_pref_id uuid [ref: > user_ui_preferences.id]
  module_name varchar(64) [not null, note: 'e.g. q_bank, q_trail, q_ledger']
  grid_id varchar(64) [not null]
  column_states json [note: 'Saved column order, visibility, and widths']
  sort_states json [note: 'Saved multi-column sorting configuration']
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]

  Note: 'Saved Tabulator.js grid layouts per forensic analytical module'
}

Table component_audit_telemetry {
  id uuid [pk, default: `uuid4()`]
  component_tag varchar(64) [not null, note: 'e.g. c-data_grid, c-chart, c-modal']
  action_type varchar(64) [not null, note: 'filter_applied, export_csv, modal_opened']
  context_module varchar(64) [not null]
  payload_json json
  timestamp timestamp [default: `now()`]

  Note: 'Forensic UI component interaction telemetry for audit trail reproducibility'
}
```

---

## 2. Django ORM Models Reference

```python
import uuid
from django.db import models
from core.models import ForensicBaseModel


class UserUIPreference(ForensicBaseModel):
    user_identifier = models.CharField(max_length=128, unique=True)
    theme = models.CharField(max_length=32, default="dark")
    grid_page_size = models.IntegerField(default=25)
    default_accent_color = models.CharField(max_length=32, default="orange")
    enable_animations = models.BooleanField(default=True)


class GridSavedLayout(ForensicBaseModel):
    user_pref = models.ForeignKey(
        UserUIPreference, on_delete=models.CASCADE, related_name="saved_layouts"
    )
    module_name = models.CharField(max_length=64)
    grid_id = models.CharField(max_length=64)
    column_states = models.JSONField(default=dict)
    sort_states = models.JSONField(default=list)


class ComponentAuditTelemetry(ForensicBaseModel):
    component_tag = models.CharField(max_length=64)
    action_type = models.CharField(max_length=64)
    context_module = models.CharField(max_length=64)
    payload_json = models.JSONField(default=dict)
```

---

## 3. Cotton Component Props & Slot Reference

### 1. `<c-base>`
Root layout shell for all pages.
* **Props:** `title` (string, page title)
* **Slots:** `{{ slot }}` (main body content)

### 2. `<c-page_header>`
Top page header with breadcrumb and actions.
* **Props:** `title`, `subtitle`, `icon`, `icon_color`, `category`, `section`
* **Slots:** `{{ slot }}` (action buttons)

### 3. `<c-stat_card>`
KPI metric summary card.
* **Props:** `title`, `value`, `subtitle`, `extra`, `icon`, `variant` (`"emerald"`, `"rose"`, `"amber"`, `"sky"`, `"slate"`)

### 4. `<c-card>`
Standard container with header.
* **Props:** `title`, `subtitle`, `icon`, `icon_color`
* **Slots:** `actions` (`<c-slot name="actions">`), `{{ slot }}` (body), `footer` (`<c-slot name="footer">`)

### 5. `<c-filter_bar>`
Multi-column filter toolbar.
* **Props:** `cols` (`"3"`, `"4"`, `"5"`, etc.)
* **Slots:** `{{ slot }}` (filter inputs), `summary` (`<c-slot name="summary">`), `actions` (`<c-slot name="actions">`)

### 6. `<c-data_grid>`
Tabulator.js table container.
* **Props:** `id`, `title`, `subtitle`, `icon`, `:columns` (JSON string), `:data` (JSON string), `pagination_size`

### 7. `<c-chart>`
Plotly visualization container.
* **Props:** `title`, `subtitle`, `icon`, `:figure_html` (rendered Plotly HTML string)

### 8. `<c-modal>`
Backdrop-blurred detail modal.
* **Props:** `id`, `title`, `subtitle`, `icon`
* **Slots:** `{{ slot }}` (modal body), `footer` (`<c-slot name="footer">`)

### 9. `<c-module_card>`
Forensic engine landing card.
* **Props:** `num`, `category`, `name`, `tag` (`"LIVE"`, `"BUILDING"`), `accent` (`"orange"`, `"gold"`, `"purple"`, `"teal"`, `"rose"`, `"amber"`, `"steel"`, `"copper"`), `href`, `tagline`
* **Slots:** `{{ slot }}` (feature list items)
