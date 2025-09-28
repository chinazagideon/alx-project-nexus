from django.core.management.base import BaseCommand
from django.utils import timezone

from feed.models import FeedItem
from feed.services import FEED_ZSET_KEY, redis_conn


class Command(BaseCommand):
    help = "Prune old feed items from Redis and database (keep newest N in Redis)"

    def add_arguments(self, parser):
        parser.add_argument("--keep", type=int, default=50000, help="Number of newest items to keep in Redis")
        parser.add_argument("--days", type=int, default=180, help="Delete DB items older than this many days")

    def handle(self, *args, **options):
        keep = options["keep"]
        days = options["days"]

        r = redis_conn()
        if r:
            total = r.zcard(FEED_ZSET_KEY)
            if total and total > keep:
                r.zremrangebyrank(FEED_ZSET_KEY, 0, total - keep - 1)
                self.stdout.write(self.style.SUCCESS(f"Redis pruned to last {keep} items"))

        cutoff = timezone.now() - timezone.timedelta(days=days)
        deleted, _ = FeedItem.objects.filter(created_at__lt=cutoff, is_active=False).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} old inactive feed items from DB"))
