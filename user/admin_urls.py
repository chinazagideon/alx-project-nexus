"""
Admin-only URL configuration for the user app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .admin_views import AdminUserViewSet

# Admin router for admin-only operations
admin_router = DefaultRouter()
admin_router.register(r"users", AdminUserViewSet, basename="admin-user")

urlpatterns = [
    path("", include(admin_router.urls)),
]
