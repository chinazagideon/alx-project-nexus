"""
URLs for the skill app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SkillViewSet, JobSkillViewSet, UserSkillViewSet

router = DefaultRouter()
router.register(r'user', UserSkillViewSet, basename='user-skill')
router.register(r"", SkillViewSet, basename="skill")

urlpatterns = [

    path("", include(router.urls)),
]
