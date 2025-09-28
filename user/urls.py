"""
URL configuration for the user app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from skill.views import UserSkillViewSet
from .email_verification import EmailVerificationView, ResendVerificationView

# Single router for all user operations
router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    path("verify-email/", EmailVerificationView.as_view(), name="verify-email"),
    path("resend-verification/", ResendVerificationView.as_view(), name="resend-verification"),
    path("", include(router.urls)),
]
