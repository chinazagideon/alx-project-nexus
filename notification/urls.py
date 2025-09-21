"""
URLs for the notification app
"""
from django.urls import path
from .views import (
    NotificationListView,
    NotificationUnreadCountView,
    NotificationMarkReadView,
    NotificationPreferenceView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread_count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('mark-read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('preferences/', NotificationPreferenceView.as_view(), name='notification-preferences'),
]


