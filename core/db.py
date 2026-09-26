"""
ForensiQ Database Performance & Concurrency Tuning
Configures SQLite WAL (Write-Ahead-Logging) mode, memory cache, and busy timeout
to enable high-concurrency background ingestion alongside active frontend polling.
"""

from django.db.backends.signals import connection_created
from django.dispatch import receiver
from loguru import logger


@receiver(connection_created)
def configure_database_connection(sender, connection, **kwargs) -> None:
    """
    Applies performance pragmas to SQLite connections.
    Safe and ignored automatically when running on MSSQL / PostgreSQL.
    """
    if connection.vendor == "sqlite":
        try:
            with connection.cursor() as cursor:
                # Enable Write-Ahead Logging (WAL) mode for multi-reader / writer concurrency
                cursor.execute("PRAGMA journal_mode = WAL;")
                # Safe synchronous level for WAL mode
                cursor.execute("PRAGMA synchronous = NORMAL;")
                # Increase busy timeout to 60 seconds to prevent 'database is locked' errors
                cursor.execute("PRAGMA busy_timeout = 60000;")
                # Set 64MB memory page cache
                cursor.execute("PRAGMA cache_size = -64000;")
                # Store temporary tables and indices in memory
                cursor.execute("PRAGMA temp_store = MEMORY;")
        except Exception as e:
            logger.debug("Failed configuring SQLite pragmas: {}", e)
