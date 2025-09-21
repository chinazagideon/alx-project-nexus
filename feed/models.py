from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class FeedItem(models.Model):
    """
    Unified feed item pointing to Jobs, Companies, or Promotions.
    """

    EVENT_JOB_POSTED = "job_posted"
    EVENT_COMPANY_JOINED = "company_joined"
    EVENT_PROMOTION_ACTIVE = "promotion_active"

    EVENT_CHOICES = (
        (EVENT_JOB_POSTED, "Job Posted"),
        (EVENT_COMPANY_JOINED, "Company Joined"),
        (EVENT_PROMOTION_ACTIVE, "Promotion Active"),
    )

    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=20, decimal_places=6)
    is_active = models.BooleanField(default=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["-score", "id"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["event_type", "is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["event_type", "content_type", "object_id"],
                condition=models.Q(is_active=True),
                name="unique_active_feed_item_per_object",
            )
        ]
        ordering = ["-score", "-id"]

    def __str__(self):
        return f"FeedItem[{self.id}] {self.event_type} -> {self.content_type.app_label}.{self.content_type.model}:{self.object_id}"


