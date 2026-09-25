# `core` — Developer Instructions & Architecture Guide

## 1. Overview & Purpose
The `core` application serves as the foundational backbone of the **ForensiQ** workstation. It provides:
1. **Shared Forensic Base Models:** Abstract Django ORM models (`ForensicBaseModel`, `UUIDModel`, `TimeStampedModel`) that all forensic analytical modules must inherit from.
2. **Workstation Security & Authentication:** Master portal authorization middleware (`PortalAuthMiddleware`), session controllers (`portal_login_view`, `portal_logout_view`), and security settings.
3. **Dynamic Engine Discovery:** Auto-discovery of all analytical modules located inside `apps/` via `core/modules.py`.
4. **Workstation Landing Dashboard:** Root landing page rendering dynamically registered forensic engines with responsive 3x centered layout.

---

## 2. Directory Structure
```
core/
├── models.py          # Abstract base models (UUID, TimeStamped, ForensicBaseModel)
├── middleware.py      # PortalAuthMiddleware enforcing master key authorization
├── modules.py         # Dynamic module auto-discovery engine
├── views.py           # landing_view, portal_login_view, portal_logout_view
├── urls.py            # Routing for / (landing), /login/, /logout/
├── templates/core/
│   ├── landing.html   # Main executive forensic workstation dashboard
│   └── login.html     # Dark-mode master access key authorization page
├── INSTRUCTION.md     # Developer guide (this file)
├── SCHEMA.md          # Shared base model specifications
└── USER_GUIDE.md      # Access control & navigation manual
```

---

## 3. Strict Rules for Interns & Vibe-Coding

> [!IMPORTANT]
> **Rule 1: Always Inherit from `ForensicBaseModel`**
> All domain models across all apps (`q_bank`, `q_trail`, etc.) MUST inherit from `core.models.ForensicBaseModel` to guarantee consistent UUID primary keys and timestamp tracking (`created_at`, `updated_at`).

> [!IMPORTANT]
> **Rule 2: Never Hardcode Module Lists**
> The landing page dynamically scans `apps/`. To register or modify a module card, configure attributes directly in `apps/<app_name>/apps.py` (`module_num`, `module_category`, `module_name`, `module_tag`, `module_accent`, `module_tagline`, `module_features`).

> [!WARNING]
> **Rule 3: Route Protection via Middleware**
> All new views are automatically protected by `PortalAuthMiddleware`. Do not bypass session checks unless adding explicit public routes to `PortalAuthMiddleware.EXEMPT_PREFIXES`.

---

## 4. How to Extend `core`

### Adding a New Shared Abstract Model
Add new abstract models to `core/models.py` with `class Meta: abstract = True`:
```python
from django.db import models
from core.models import ForensicBaseModel


class ForensicAuditLogModel(ForensicBaseModel):
    investigator_id = models.CharField(max_length=120, default="system_auditor")
    action_note = models.TextField(blank=True)

    class Meta:
        abstract = True
```
