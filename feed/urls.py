"""
URLs for the feed app
"""

from django.urls import path
from .views import FeedListView

urlpatterns = [
    path("", FeedListView.as_view(), name="feed-list"),
]
