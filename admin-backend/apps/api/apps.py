from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api'
    label = 'xxgcms_api'

    def ready(self):
        import apps.api.ai.providers  # noqa: F401 — register AI providers
