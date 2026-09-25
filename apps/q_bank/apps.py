from django.apps import AppConfig


class QBankConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "q_bank"
    verbose_name = "Q-Bank"

    # Forensic Module Metadata
    module_num = "01"
    module_category = "MONEY"
    module_name = "Bank"
    module_tag = "LIVE"
    module_accent = "orange"
    module_tagline = "Reads statements. Flags keywords."
    module_features = [
        "Flagged transactions, vendor & party summary",
        "Tuneable watchlist per investigation",
    ]
    module_url = "/demo/tabulator/"
    module_order = 1
