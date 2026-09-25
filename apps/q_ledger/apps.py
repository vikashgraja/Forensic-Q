from django.apps import AppConfig


class QLedgerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "q_ledger"
    verbose_name = "Q-Ledger"

    # Forensic Module Metadata (Under Construction)
    module_num = ""
    module_category = "ERP / RECORDS"
    module_name = "Ledger"
    module_tag = "BUILDING"
    module_accent = "copper"
    module_tagline = "SAP / ERP anomalies · PO · GRN · invoice."
    module_features = []
    module_url = "/demo/tabulator/"
    module_order = 8
