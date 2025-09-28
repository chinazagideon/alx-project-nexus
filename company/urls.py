"""
URL configuration for the company app
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CompanyViewSet

router = DefaultRouter()
router.register(r"", CompanyViewSet, basename="company")

urlpatterns = [
    path("", include(router.urls)),
]
