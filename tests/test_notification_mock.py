import pytest
from django.test import TestCase
from django.apps import apps

# Get the model from the app registry to ensure we get the mock version
Notification = apps.get_model("notification", "Notification")


class TestNotificationMock(TestCase):
    """Test that the mock notification app is working correctly."""

    def test_notification_model_exists(self):
        """Test that we can import and use the mock Notification model."""
        # This should work with the mock model
        notification = Notification.objects.create(user_id=1, event_type="test_event", status="unread")

        self.assertEqual(notification.user_id, 1)
        self.assertEqual(notification.event_type, "test_event")
        self.assertEqual(notification.status, "unread")
        self.assertIsNotNone(notification.created_at)

    def test_notification_queryset_works(self):
        """Test that we can query the mock Notification model."""
        # Create a few notifications
        Notification.objects.create(user_id=1, event_type="test1", status="unread")
        Notification.objects.create(user_id=2, event_type="test2", status="read")

        # Test queries work
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(Notification.objects.filter(user_id=1).count(), 1)
        self.assertEqual(Notification.objects.filter(status="read").count(), 1)
