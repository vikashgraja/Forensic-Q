# Django Architecture & Code Style Rules

## 1. Domain Separation (Services & Selectors)
- **`models.py`**: Clean declarative models inheriting from `core.models.ForensicBaseModel`. Implement `__str__()` on all models. No complex business logic in `save()`.
- **`selectors.py`**: All read-only database queries. Always eliminate N+1 queries with `select_related()` and `prefetch_related()`. No database writes in selectors.
- **`services.py`**: All business logic, scoring, file ingestion, and mutations. Decorate multi-model writes with `@transaction.atomic`.
- **`views.py`**: Thin controllers. Only parse HTTP requests, invoke selectors/services, and render Cotton templates or JSON.

## 2. Django Cotton Template Guidelines
- Always use `<c-slot name="actions">` instead of `<c-slot:actions>` to ensure Windows compatibility (`WinError 123`).
- Keep components modular and leverage design system tokens defined in `ui/`.

## 3. Database & Migrations
- Model schemas must match the DBML specifications in each app's `SCHEMA.md` ([dbdiagram.io](https://dbdiagram.io)).
- Never commit model changes without generating migration files (`uv run python manage.py makemigrations`).
