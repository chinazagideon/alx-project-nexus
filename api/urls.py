"""
URL configuration for api app.
"""

from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import LogoutAllView, LoginView, RefreshView, LogoutView
from two_factor.urls import urlpatterns as two_factor_patterns


# Authentication endpoints
auth_patterns = [
    path("auth/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", RefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="token_logout"),
    path("auth/logout-all/", LogoutAllView.as_view(), name="token_logout_all"),
]

# All other endpoints
urlpatterns = [
    # Authentication endpoints
    *auth_patterns,
    # Admin endpoints (admin only)
    path("admin/", include("user.admin_urls")),  # Admin user management
    # All other endpoints (with conditional permissions)
    path("users/", include("user.urls")),  # User management (includes registration)
    path("skills/", include("skill.urls")),  # Skills (public read, auth write)
    path("companies/", include("company.urls")),  # Companies
    path("jobs/", include("job.urls")),  # Jobs
    path("uploads/", include("upload.urls")),  # File uploads
    path("promotions/", include("promotion.urls")),  # Promotions
    path("applications/", include("application.urls")),  # Job applications
    path("addresses/", include("address.urls")),  # Address management
    path("notifications/", include("notification.urls")),  # Notifications
    path("feed/", include("feed.urls")),  # Feed
    path("mfa/", include(two_factor_patterns[0])),
]
