from django.apps import AppConfig


class QVoiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'q_voice'
    verbose_name = 'Q-Voice'

    # Forensic Module Metadata (Under Construction)
    module_num = ""
    module_category = "VOICE"
    module_name = "Voice"
    module_tag = "BUILDING"
    module_accent = "steel"
    module_tagline = "Call transcripts · entities · intent flags."
    module_features = []
    module_url = "/demo/sandbox/"
    module_order = 7
