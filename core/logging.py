"""
ForensiQ Centralized Loguru Logging System
Integrates Loguru with Django, background workers, and standard library logging.
"""

import logging
import sys
from pathlib import Path

from django.conf import settings
from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Redirects standard library logging records to Loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            if frame.f_back:
                frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """
    Initializes Loguru sinks (colorized console + rotating file log)
    and intercepts standard logging.
    """
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Console sink
    is_debug = getattr(settings, "DEBUG", True)
    logger.add(
        sys.stderr,
        format=log_format,
        level="DEBUG" if is_debug else "INFO",
        colorize=True,
    )

    # Rotating file sink
    base_dir = getattr(settings, "BASE_DIR", Path.cwd())
    log_dir = Path(base_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "forensiq_{time:YYYY-MM-DD}.log"

    logger.add(
        str(log_file),
        format=log_format,
        level="DEBUG",
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )

    # Intercept standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for logger_name in ("django", "django.server", "django.request", "django.db.backends"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
