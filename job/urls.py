"""
URL configuration for the jobs app
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from skill.views import JobSkillViewSet

from .views import JobViewSet, job_search, job_stats, search_facets, search_suggestions

router = DefaultRouter()
# Mount jobs at the root of this app's URLConf
router.register(r"skill", JobSkillViewSet, basename="job-skill")
router.register(r"", JobViewSet, basename="job")


urlpatterns = [
    # Search endpoints
    path("search/", job_search, name="job-search"),
    path("search/suggestions/", search_suggestions, name="search-suggestions"),
    path("search/facets/", search_facets, name="search-facets"),
    path("stats/", job_stats, name="job-stats"),
    # path(
    #     "skills/",
    #     JobSkillViewSet.as_view({"get": "list", "post": "create", "delete": "destroy"}),
    #     name="Jobs skills",
    # ),
    # Job CRUD endpoints
    path("", include(router.urls)),
]
