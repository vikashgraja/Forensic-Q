from django.apps import AppConfig


class QLinkConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "q_link"
    verbose_name = "Q-Link"

    # Forensic Module Metadata
    module_num = "06"
    module_category = "CORRELATOR"
    module_name = "Link"
    module_tag = "BUILDING"
    module_accent = "amber"
    module_tagline = "Joins the dots across modules."
    module_features = [
        "Integrated evidence map",
        "The bigger investigation picture",
    ]
    module_url = "/demo/tabulator/"
    module_order = 6
