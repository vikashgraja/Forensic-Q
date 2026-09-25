from django.apps import AppConfig


class QVerifyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "q_verify"
    verbose_name = "Q-Verify"

    # Forensic Module Metadata
    module_num = "05"
    module_category = "DOCUMENT"
    module_name = "Verify"
    module_tag = "BUILDING"
    module_accent = "rose"
    module_tagline = "Catches the quiet edit."
    module_features = [
        "Metadata report, suspicious/edited files",
        "Authenticity indicators across formats",
    ]
    module_url = "/demo/sandbox/"
    module_order = 5
