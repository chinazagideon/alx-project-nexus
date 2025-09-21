from django.db import models

class Notification(models.Model):
    """
    Mock Notification Model
    """
    # minimal shape needed for your tests
    user_id = models.IntegerField()
    event_type = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, blank=True, default="unread")
    created_at = models.DateTimeField(auto_now_add=True)