import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from user.models.models import User

logger = logging.getLogger(__name__)


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


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_verification(self, user_id):
    """
    Send email verification to user
    """
    try:
        user = User.objects.get(id=user_id)

        # Generate verification token if not exists
        token = user.generate_email_verification_token()

        # Prepare email content
        subject = "Verify Your Email - Connect Hire"

        # Simple HTML email template
        html_message = f"""
        <html>
        <body>
            <h2>Welcome to Connect Hire!</h2>
            <p>Hi {user.get_full_name()},</p>
            <p>Thank you for registering with Connect Hire. Please verify your email address to complete your registration.</p>
            
            <p>Your Verification Token is:</p>
            <p>{token}</p>
           
            <p>This token will expire in 24 hours.</p>
            <p>Best regards,<br>The Connect Hire Team</p>
        </body>
        </html>
        """

        # Plain text version
        text_message = f"""
        Welcome to Connect Hire!
        
        Hi {user.get_full_name()},
        
        Thank you for registering with Connect Hire. Please verify your email address to complete your registration.
        
        Your Verification Token is: {token}
        
        This token will expire in 24 hours.
        
        Best regards,
        The Connect Hire Team
        """

        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        # Update the sent timestamp
        user.email_verification_sent_at = timezone.now()
        user.save(update_fields=["email_verification_sent_at"])

        logger.info(f"Email verification sent to user {user.id} ({user.email})")

    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found for email verification")
    except Exception as exc:
        logger.error(f"Failed to send email verification to user {user_id}: {str(exc)}")
        raise self.retry(exc=exc)
