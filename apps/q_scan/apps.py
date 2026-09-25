from django.apps import AppConfig


class QScanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'q_scan'
    verbose_name = 'Q-Scan'

    # Forensic Module Metadata
    module_num = "04"
    module_category = "DESKTOP"
    module_name = "Scan"
    module_tag = "LIVE"
    module_accent = "teal"
    module_tagline = "Walks drives. Highlights hits."
    module_features = [
        "Relevant files, keyword hits",
        "Evidence locations across the workstation",
    ]
    module_url = "/demo/tabulator/"
    module_order = 4
