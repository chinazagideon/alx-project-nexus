from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from job_portal.settings import AUTH_USER_MODEL


class NotificationChannel(models.IntegerChoices):
    """
    Notification channel choices
    """

    IN_APP = 1, "in_app"
    EMAIL = 2, "email"
    PUSH = 4, "push"


class NotificationStatus(models.TextChoices):
    """
    Notification status choices
    """

    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    READ = "read", "Read"
    DISMISSED = "dismissed", "Dismissed"


class Notification(models.Model):
    """
    Notification model
    """

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    event_type = models.CharField(max_length=100)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    actor_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True, related_name="actor_notifs"
    )
    actor_object_id = models.PositiveIntegerField(null=True, blank=True)

    channels = models.IntegerField(default=NotificationChannel.IN_APP)
    status = models.CharField(max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)

    title = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    data = models.JSONField(default=dict, blank=True)
    dedupe_key = models.CharField(max_length=255, blank=True)

    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status", "created_at"]),
            models.Index(fields=["dedupe_key"]),
        ]
        ordering = ["-created_at", "-id"]

    def mark_read(self):
        """
        Mark the notification as read
        """
        self.status = NotificationStatus.READ
        self.read_at = timezone.now()
        self.save(update_fields=["status", "read_at", "updated_at"])


class NotificationPreference(models.Model):
    """
    Notification preference model
    """

    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_pref")
    in_app_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=64, default="UTC")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
