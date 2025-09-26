from django.shortcuts import render
from rest_framework import viewsets
from application.models import Application
from application.serializers import ApplicationSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.pagination import DefaultPagination
from drf_spectacular.utils import extend_schema


class ApplicationsViewSet(viewsets.ModelViewSet):
    """
    viewset for application model
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    # hide the endpoints from docs
    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        """Hide the DELETE endpoint from docs"""
        return super().destroy(request, *args, **kwargs)
    
    # hide the endpoints from docs
    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        """Hide the PUT endpoint from docs"""
        return super().update(request, *args, **kwargs)

    # hide the endpoints from docs
    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        """Hide the PATCH endpoint from docs"""
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        """
        Get the queryset for applications based on user role:
        - TALENT users see only their own applications
        - RECRUITER users see applications for jobs they own (through their company)
        - ADMIN users see all applications
        """
        user = self.request.user
        
        if user.role == 'admin':
            # Admin can see all applications
            return Application.objects.all()
        elif user.role == 'talent':
            # Talent users see only their own applications
            return Application.objects.filter(user=user)
        elif user.role == 'recruiter':
            # Recruiters see applications for jobs they own (through their company)
            return Application.objects.filter(job__company__user=user)
        else:
            # Default fallback - return empty queryset for unknown roles
            return Application.objects.none()