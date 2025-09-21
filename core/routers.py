"""
Custom API routers for better organization and documentation
"""

from rest_framework.routers import DefaultRouter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class CustomRouter(DefaultRouter):
    """
    Custom router that adds common parameters and better documentation
    """
    
    def get_api_root_view(self, api_urls=None):
        """
        Return a basic root view.
        """
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        
        return self.APIRootView.as_view(api_root_dict=api_root_dict)


class AuthRouter(CustomRouter):
    """
    Router specifically for authentication-related endpoints
    """
    
    def register(self, prefix, viewset, basename=None):
        """
        Register viewset with authentication-specific configuration
        """
        super().register(prefix, viewset, basename)
        
        # Add common authentication parameters
        if hasattr(viewset, 'get_extra_action_kwargs'):
            extra_kwargs = viewset.get_extra_action_kwargs()
            extra_kwargs.setdefault('permission_classes', [])
            extra_kwargs.setdefault('authentication_classes', [])


class PublicRouter(CustomRouter):
    """
    Router for public endpoints that don't require authentication
    """
    
    def register(self, prefix, viewset, basename=None):
        """
        Register viewset with public access configuration
        """
        super().register(prefix, viewset, basename)
        
        # Ensure public endpoints are properly documented
        if hasattr(viewset, 'get_extra_action_kwargs'):
            extra_kwargs = viewset.get_extra_action_kwargs()
            extra_kwargs.setdefault('permission_classes', [])
