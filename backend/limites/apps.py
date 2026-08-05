from django.apps import AppConfig


class LimitesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "limites"

    def ready(self):
        from . import sinais  # noqa: F401
