from django.apps import AppConfig


class QVoiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "q_voice"
    verbose_name = "Q-Voice"

    # Forensic Module Metadata (In Development)
    module_num = "07"
    module_category = "VOICE"
    module_name = "Voice"
    module_tag = "BUILDING"
    module_accent = "steel"
    module_tagline = "Transcribes speech. Flags intent."
    module_features = [
        "Call transcripts, entity & speaker matrix",
        "Concealment and intent detection",
    ]
    module_url = "/demo/sandbox/"
    module_order = 7
