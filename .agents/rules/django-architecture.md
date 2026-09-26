# Django Architecture & Code Style Rules

## 1. Domain Separation (4-Tier Architecture)
- **`backend/`**: Dedicated forensic analysis scripts, parsers, classifiers, and algorithmic calculations. Kept independent from Django web request lifecycles.
- **`models.py`**: Clean declarative models inheriting from `core.models.ForensicBaseModel`. Implement `__str__()` on all models. No complex business logic in `save()`.
- **`selectors.py`**: All read-only database queries. Always eliminate N+1 queries with `select_related()` and `prefetch_related()`. No database writes in selectors.
- **`services.py`**: All business workflows, file ingestion orchestration, and mutations calling `backend/`. Decorate multi-model writes with `@transaction.atomic`.
- **`views.py`**: Thin controllers. Only parse HTTP requests, invoke selectors/services, and render Cotton templates or JSON.

## 2. Django Cotton Template Guidelines
- Always use `<c-slot name="actions">` instead of `<c-slot:actions>` to ensure Windows compatibility (`WinError 123`).
- Keep components modular and leverage design system tokens defined in `ui/`.

## 3. Database & Migrations
- Model schemas must match the DBML specifications in each app's `SCHEMA.md` ([dbdiagram.io](https://dbdiagram.io)).
- Never commit model changes without generating migration files (`uv run python manage.py makemigrations`).

## 4. Logging Standards (Loguru)
- Always use `from loguru import logger` instead of standard `logging.getLogger(__name__)`.
- Logging output is centralized in `core/logging.py` (colorized console + rotating file logs under `logs/`).
- Never swallow exceptions with bare `pass` or `continue` (Bandit `B110`, `B112`); always log them with `logger.debug(...)` or `logger.warning(...)`.

## 5. Large File Uploads & Forensic Ingestion (50+ GB)
- Massive evidence files (PSTs, disk images, PCAPs, bank databases) must use `core.file_uploader.FileUploader` for resumable binary chunking to disk.
- Compute SHA-256 evidence chain of custody hashes automatically during streaming.
- Process large files in background threads with progress callbacks, flushing database records in batches of 250 via `bulk_create()` wrapped in `@transaction.atomic`.
