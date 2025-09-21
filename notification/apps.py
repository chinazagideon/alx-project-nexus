from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notification"

    def ready(self):
        # import signals
        from . import signals  # noqa: F401


