from django.apps import AppConfig
from two_factor.signals import user_verified


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user"

    def ready(self):
        user_verified.connect(notify_two_factor_setup)


def notify_two_factor_setup(sender, request, user, device, **kwargs):
    """
    Notify User when two factor is setup
    """
    from notification.tasks import send_otp_notification

    send_otp_notification.delay(
        to_email=user.email,
        subject="Two Factor Authentication Setup",
        message="Your two factor authentication has been setup successfully.",
    )
