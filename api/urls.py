"""
URL configuration for api app.
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from .views import ProtectedView


urlpatterns = [
    path('jobs/', include('job.urls')),
    path('uploads/', include('upload.urls')),
    path('promotions/', include('promotion.urls')),
    path('application', include('application.urls')),
    path('users/', include('user.urls')),
    path('addresses/', include('address.urls')),
    path('companies/', include('company.urls')),
    path('skills/', include('skill.urls')),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('protected/', ProtectedView.as_view(), name='protected'),
]