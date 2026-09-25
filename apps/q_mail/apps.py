from django.apps import AppConfig


class QMailConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "q_mail"
    verbose_name = "Q-Mail"

    # Forensic Module Metadata
    module_num = "03"
    module_category = "COMMUNICATIONS"
    module_name = "Mail"
    module_tag = "BUILDING"
    module_accent = "purple"
    module_tagline = "PST at the speed of audit."
    module_features = [
        "Emails, attachments, communication links",
        "Keyword hits across threads",
    ]
    module_url = "/demo/sandbox/"
    module_order = 3
