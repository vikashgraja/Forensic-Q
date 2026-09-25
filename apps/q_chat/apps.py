from django.apps import AppConfig


class QChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "q_chat"
    verbose_name = "Q-Chat"

    # Forensic Module Metadata (Under Construction)
    module_num = ""
    module_category = "COMMUNICATIONS"
    module_name = "Chat"
    module_tag = "BUILDING"
    module_accent = "steel"
    module_tagline = "Teams & corporate chat search · threads."
    module_features = []
    module_url = "/demo/sandbox/"
    module_order = 9
