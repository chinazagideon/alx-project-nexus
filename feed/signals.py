from typing import Optional

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from job.models import Job
from company.models import Company
from promotion.models import Promotion, PromotionPlacement, PromotionStatus

from .models import FeedItem
from .services import calculate_score, zadd_feed, zrem_feed


def _create_or_update_feed_item(event_type: str, instance, bonus: int = 0) -> Optional[FeedItem]:
    """
    Create or update a feed item
    """
    ct = ContentType.objects.get_for_model(instance.__class__)
    score = calculate_score(bonus=bonus)
    feed_item, created = FeedItem.objects.update_or_create(
        event_type=event_type,
        content_type=ct,
        object_id=instance.id,
        defaults={
            "score": score,
            "is_active": True,
        },
    )
    zadd_feed(feed_item.id, float(score))
    return feed_item


def _deactivate_feed_item(event_type: str, instance) -> None:
    """
    Deactivate a feed item
    """
    ct = ContentType.objects.get_for_model(instance.__class__)
    FeedItem.objects.filter(event_type=event_type, content_type=ct, object_id=instance.id, is_active=True).update(
        is_active=False
    )
    for fi in FeedItem.objects.filter(event_type=event_type, content_type=ct, object_id=instance.id):
        zrem_feed(fi.id)


@receiver(post_save, sender=Job)
def job_posted_feed(sender, instance: Job, created: bool, **kwargs):
    """
    Job posted feed
    """
    if created:
        # Only include if not closed
        if not instance.close_date or instance.close_date >= timezone.now():
            _create_or_update_feed_item(FeedItem.EVENT_JOB_POSTED, instance, bonus=100_000)


@receiver(post_save, sender=Company)
def company_joined_feed(sender, instance: Company, created: bool, **kwargs):
    """
    Company joined feed
    """
    if created and instance.status:
        _create_or_update_feed_item(FeedItem.EVENT_COMPANY_JOINED, instance, bonus=50_000)


@receiver(post_save, sender=Promotion)
def promotion_activated_feed(sender, instance: Promotion, created: bool, **kwargs):
    """
    Promotion activated feed
    """
    # Add when promotion is ACTIVE and placed in FEED
    if instance.placement == PromotionPlacement.FEED and instance.status == PromotionStatus.ACTIVE:
        bonus = 1_000_000 * getattr(instance.package, "priority_weight", 1)
        _create_or_update_feed_item(FeedItem.EVENT_PROMOTION_ACTIVE, instance, bonus=bonus)
    elif instance.status in {PromotionStatus.EXPIRED, PromotionStatus.CANCELLED}:
        _deactivate_feed_item(FeedItem.EVENT_PROMOTION_ACTIVE, instance)
