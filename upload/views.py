"""
Views for the upload app
"""
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import UploadSerializer
from .models import Upload

class UploadViewSet(viewsets.ModelViewSet):
    """
    View for listing and creating files
    """
    serializer_class = UploadSerializer
    permission_classes = [IsAuthenticated]
    queryset = Upload.objects.all()