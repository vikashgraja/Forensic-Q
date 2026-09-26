from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self) -> None:
        import core.db  # noqa: F401
        from core.logging import setup_logging

        setup_logging()
