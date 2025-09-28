from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from job.models import Job
from company.models import Company
from promotion.models import Promotion, PromotionPlacement, PromotionStatus

from feed.models import FeedItem
from feed.services import calculate_score, zadd_feed


class Command(BaseCommand):
    help = "Rebuild the global feed from existing data and repopulate Redis"

    def handle(self, *args, **options):
        FeedItem.objects.all().delete()

        # Jobs
        now = timezone.now()
        for job in Job.objects.all():
            if not job.close_date or job.close_date >= now:
                fi = FeedItem.objects.create(
                    event_type=FeedItem.EVENT_JOB_POSTED,
                    content_type=ContentType.objects.get_for_model(Job),
                    object_id=job.id,
                    score=calculate_score(bonus=100_000),
                    is_active=True,
                )
                zadd_feed(fi.id, float(fi.score))

        # Companies
        for company in Company.objects.filter(status=True):
            fi = FeedItem.objects.create(
                event_type=FeedItem.EVENT_COMPANY_JOINED,
                content_type=ContentType.objects.get_for_model(Company),
                object_id=company.id,
                score=calculate_score(bonus=50_000),
                is_active=True,
            )
            zadd_feed(fi.id, float(fi.score))

        # Promotions
        for promo in Promotion.objects.filter(placement=PromotionPlacement.FEED, status=PromotionStatus.ACTIVE):
            bonus = 1_000_000 * getattr(promo.package, "priority_weight", 1)
            fi = FeedItem.objects.create(
                event_type=FeedItem.EVENT_PROMOTION_ACTIVE,
                content_type=ContentType.objects.get_for_model(Promotion),
                object_id=promo.id,
                score=calculate_score(bonus=bonus),
                is_active=True,
            )
            zadd_feed(fi.id, float(fi.score))

        self.stdout.write(self.style.SUCCESS("Feed rebuilt and Redis populated."))
