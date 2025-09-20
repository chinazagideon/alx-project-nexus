"""
URL configuration for the user app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from skill.views import UserSkillViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'skill', UserSkillViewSet, basename='user-skill')

urlpatterns = [
    path('', include(router.urls)),
]