from django.apps import AppConfig


class QChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "q_chat"
    verbose_name = "Q-Chat"

    # Forensic Module Metadata (In Development)
    module_num = "09"
    module_category = "COMMUNICATIONS"
    module_name = "Chat"
    module_tag = "BUILDING"
    module_accent = "steel"
    module_tagline = "Reconstructs team chat threads."
    module_features = [
        "Teams, Slack & WhatsApp thread correlation",
        "Off-the-record chat keyword alerts",
    ]
    module_url = "/demo/sandbox/"
    module_order = 9
