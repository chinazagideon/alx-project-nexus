from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from job.models import Job
from company.models import Company
from promotion.models import Promotion, PromotionStatus
from user.models.models import User

from .models import Notification, NotificationChannel, NotificationStatus
from .services import incr_unread


from .enums import CustomMessage


def _notify(
    user_id: int, event_type: str, title: str, body: str, content_object=None, data=None
):
    """
    Notify a user
    """
    notif = Notification.objects.create(
        user_id=user_id,
        event_type=event_type,
        title=title,
        body=body,
        data=data or {},
        channels=NotificationChannel.IN_APP,
        status=NotificationStatus.PENDING,
    )
    incr_unread(user_id, 1)
    return notif


@receiver(post_save, sender=Job)
def on_job_created(sender, instance: Job, created: bool, **kwargs):
    """
    Job created signal
    """
    if created:
        company_owner_id = getattr(instance.company, "user_id", None)
        if company_owner_id:
            _notify(
                user_id=company_owner_id,
                event_type="job_posted",
                title="Your job was posted",
                body=CustomMessage.JOB_CREATED_TXT.value.format(
                    job_title=instance.title, 
                    company_name=instance.company.name
                ),
                content_object=instance,
                data={"job_id": instance.id},
            )


@receiver(post_save, sender=Company)
def on_company_created(sender, instance: Company, created: bool, **kwargs):
    """
    Company created signal
    """
    if created and getattr(instance, "user_id", None):
        _notify(
            user_id=instance.user_id,
            event_type="company_created",
            title="Company created",
            body=CustomMessage.COMPANY_CREATED_TXT.value.format(company_name=instance.name),
            content_object=instance,
            data={"company_id": instance.id},
        )


@receiver(post_save, sender=Promotion)
def on_promotion_updated(sender, instance: Promotion, created: bool, **kwargs):
    """
    Signal promotion updated
    """
    if instance.status == PromotionStatus.ACTIVE:
        owner_id = getattr(instance, "owner_id", None)
        if owner_id:
            _notify(
                user_id=owner_id,
                event_type="promotion_active",
                title="Promotion active",
                body=CustomMessage.PROMOTION_ACTIVE_TXT.value.format(promotion_name=instance.name),
                content_object=instance,
                data={"promotion_id": instance.id},
            )
