from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_otp_notification(self, to_email, subject, message):
    """
    Send OTP notification
    """

    try: 
        send_mail(
            subject, 
            message, 
            settings.DEFAULT_FROM_EMAIL, 
            [to_email],
            fail_silently=False,
            )
    except Exception as exec:
        raise self.retry(exec=exec)