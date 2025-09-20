""" 
URL configuration for the upload app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UploadViewSet

router = DefaultRouter()
router.register(r'', UploadViewSet, basename='upload')
# router.register(r'list', UploadListView, basename='upload-list')
# router.register(r'detail', UploadDetailView, basename='upload-detail')

urlpatterns = [
    # path("uploads/", UploadView.as_view(), name="upload-create"),
    # path("uploads/", UploadListView.as_view(), name="upload-list"),
    # path("uploads/<int:pk>/", UploadDetailView.as_view(), name="upload-detail"),
    path('', include(router.urls)),
]
