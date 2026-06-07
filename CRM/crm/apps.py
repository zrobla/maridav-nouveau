from django.conf import settings
from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "crm"
    verbose_name = "CRM"

    def ready(self):
        self.verbose_name = getattr(settings, "CRM_PLATFORM_NAME", self.verbose_name)
        from . import signals  # noqa: F401
