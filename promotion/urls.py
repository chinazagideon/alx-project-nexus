from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PromotionPackageViewSet, PromotionViewSet

router = DefaultRouter()
# Mount promotions at the root of this app's URLConf to avoid duplicate segment
router.register(r"", PromotionViewSet, basename="promotions")
router.register(r"packages", PromotionPackageViewSet, basename="promotion-package")


urlpatterns = [
    path("", include(router.urls)),
]
