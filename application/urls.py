"""
URL configuration for the application app
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ApplicationsViewSet

router = DefaultRouter()
router.register(r"", ApplicationsViewSet, basename="application")

urlpatterns = [
    path("", include(router.urls)),
]
