"""
URL configuration for the user app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from skill.views import UserSkillViewSet

# Single router for all user operations
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]