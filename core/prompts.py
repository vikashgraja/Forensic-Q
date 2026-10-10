"""
Core Prompt Management & Template Engine
=============================================================================
Centralizes prompt asset resolution, template rendering, and caching for all
forensic AI and LLM agents in ForensiQ.

Decouples natural language prompt engineering from Python business logic so
prompts can be inspected, calibrated, and maintained independently in `apps/<q_app>/prompts/`.
=============================================================================
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from django.conf import settings
from loguru import logger

# Base directory for all decoupled prompt templates
_DEFAULT_PROMPTS_DIR = (
    Path(getattr(settings, "BASE_DIR", Path(__file__).resolve().parent.parent)) / "prompts"
)
PROMPTS_DIR: Path = Path(getattr(settings, "PROMPTS_DIR", _DEFAULT_PROMPTS_DIR))


def get_prompt_path(app_name: str, filename: str) -> Path:
    """
    Resolves the filesystem path for a specific prompt template file.
    Searches first in the localized `apps/<app_name>/prompts/<filename>` directory,
    and falls back to `prompts/<app_name>/<filename>` if present.
    """
    base_dir = Path(getattr(settings, "BASE_DIR", Path(__file__).resolve().parent.parent))
    clean_app = app_name.replace("apps/", "").replace("apps\\", "").strip()

    app_path = base_dir / "apps" / clean_app / "prompts" / filename
    if app_path.exists():
        return app_path

    # Fallback to root prompts directory if present
    root_path = base_dir / "prompts" / clean_app / filename
    if root_path.exists():
        return root_path

    return app_path


@lru_cache(maxsize=128)
def load_prompt(app_name: str, filename: str, fallback: str = "") -> str:
    """
    Loads raw prompt text from disk with LRU caching.
    Returns `fallback` if the prompt file does not exist or cannot be read.
    """
    path = get_prompt_path(app_name, filename)
    if not path.is_file():
        if fallback:
            logger.debug(
                f"[Prompts] Template '{app_name}/{filename}' not found at {path}. Using fallback."
            )
            return fallback.strip()
        logger.warning(f"[Prompts] Missing prompt template: {path}")
        return ""

    try:
        content = path.read_text(encoding="utf-8").strip()
        return content
    except Exception as err:
        logger.error(f"[Prompts] Error reading prompt template '{path}': {err}")
        return fallback.strip() if fallback else ""


def render_prompt(
    app_name: str,
    filename: str,
    fallback: str = "",
    context: dict[str, Any] | None = None,
    **kwargs: Any,
) -> str:
    """
    Loads a prompt template and substitutes named placeholders using kwargs and context.
    If formatting fails (e.g. key error), gracefully falls back or logs an error.
    """
    template = load_prompt(app_name, filename, fallback=fallback)
    if not template:
        return ""

    params = {}
    if context:
        params.update(context)
    if kwargs:
        params.update(kwargs)

    try:
        return template.format(**params)
    except KeyError as missing_key:
        logger.warning(
            f"[Prompts] Missing placeholder {missing_key} when rendering '{app_name}/{filename}'."
        )
        # Attempt safe replacement: leave unformatted tokens intact if possible
        import string

        class SafeDict(dict):
            def __missing__(self, key):
                return f"{{{key}}}"

        formatter = string.Formatter()
        return formatter.vformat(template, (), SafeDict(**params))
    except Exception as err:
        logger.error(f"[Prompts] Failed formatting template '{app_name}/{filename}': {err}")
        return template


def clear_prompt_cache() -> None:
    """Clears the in-memory LRU prompt cache (useful during testing or live prompt editing)."""
    load_prompt.cache_clear()
