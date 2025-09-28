from django.core.management.base import BaseCommand
from django.utils import timezone

from promotion.models import Promotion, PromotionStatus


class Command(BaseCommand):
    help = "Expire promotions whose end_at is in the past and status is ACTIVE"

    def handle(self, *args, **options):
        now = timezone.now()
        expired = Promotion.objects.filter(status=PromotionStatus.ACTIVE, end_at__lt=now).update(
            status=PromotionStatus.EXPIRED
        )
        self.stdout.write(self.style.SUCCESS(f"Expired {expired} promotions"))
