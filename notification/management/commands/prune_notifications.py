from django.core.management.base import BaseCommand
from django.utils import timezone

from notification.models import Notification, NotificationStatus


class Command(BaseCommand):
    help = "Prune old read notifications from database"

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=180)

    def handle(self, *args, **options):
        days = options["days"]
        cutoff = timezone.now() - timezone.timedelta(days=days)
        deleted, _ = Notification.objects.filter(status=NotificationStatus.READ, created_at__lt=cutoff).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} old read notifications"))
