"""
Permission configuration for all viewsets and endpoints.
This centralizes permission management for better maintainability.
"""

from core.permissions_enhanced import (
    IsOwnerOrReadOnly,
    IsOwnerOrStaff,
    IsOwnerOrStaffOrReadOnly,
    IsOwnerOrStaffForList,
    PublicReadAuthenticatedWrite,
    IsAdminOrReadOnly,
    IsAdminOnly,
    IsRecruiterOrAdmin,
    IsTalentOrAdmin,
    IsJobOwnerOrStaff,
    IsCompanyOwnerOrStaff,
    IsApplicationOwnerOrJobOwnerOrStaff,
    IsUploadOwnerOrStaff,
    IsAddressOwnerOrStaff,
    IsOwnerOrJobOwnerOrStaff,
    IsOwnerOrJobOwnerOrStaffForCreate,
    RoleBasedPermission,
)
from rest_framework import permissions

# Permission configurations for each app
PERMISSION_CONFIG = {
    "user": {
        "UserViewSet": {
            "list": [IsAdminOnly],
            "retrieve": [IsOwnerOrStaffForList],
            "create": [permissions.AllowAny],  # Registration
            "update": [IsOwnerOrStaffForList],
            "partial_update": [IsOwnerOrStaffForList],
            "destroy": [IsAdminOnly],
            "profile": [permissions.IsAuthenticated],
            "update_profile_put": [permissions.IsAuthenticated],
            "update_profile_patch": [permissions.IsAuthenticated],
        }
    },
    "job": {
        "JobListCreateView": {
            "list": [permissions.IsAuthenticated],
            "create": [IsRecruiterOrAdmin],
        },
        "JobViewSet": {
            "list": [permissions.IsAuthenticated],
            "retrieve": [permissions.IsAuthenticated],
            "create": [IsRecruiterOrAdmin],
            "update": [IsJobOwnerOrStaff],
            "partial_update": [IsJobOwnerOrStaff],
            "destroy": [IsJobOwnerOrStaff],
        },
        "job_search": [permissions.IsAuthenticated],
        "search_suggestions": [permissions.IsAuthenticated],
        "search_facets": [permissions.IsAuthenticated],
        "job_stats": [permissions.IsAuthenticated],
    },
    "application": {
        "ApplicationsViewSet": {
            "list": [permissions.IsAuthenticated],
            "retrieve": [IsApplicationOwnerOrJobOwnerOrStaff],
            "create": [IsTalentOrAdmin],
            "update": [IsApplicationOwnerOrJobOwnerOrStaff],
            "partial_update": [IsApplicationOwnerOrJobOwnerOrStaff],
            "destroy": [IsApplicationOwnerOrJobOwnerOrStaff],
        }
    },
    "company": {
        "CompanyViewSet": {
            "list": [permissions.IsAuthenticated],
            "retrieve": [permissions.IsAuthenticated],
            "create": [IsRecruiterOrAdmin],
            "update": [IsCompanyOwnerOrStaff],
            "partial_update": [IsCompanyOwnerOrStaff],
            "destroy": [IsCompanyOwnerOrStaff],
        }
    },
    "skill": {
        "SkillViewSet": {
            "list": [PublicReadAuthenticatedWrite],
            "retrieve": [PublicReadAuthenticatedWrite],
            "create": [IsAdminOnly],
            "update": [IsAdminOnly],
            "partial_update": [IsAdminOnly],
            "destroy": [IsAdminOnly],
        },
        "JobSkillViewSet": {
            "list": [permissions.IsAuthenticated],
            "retrieve": [permissions.IsAuthenticated],
            "create": [IsOwnerOrJobOwnerOrStaffForCreate],
            "update": [IsOwnerOrJobOwnerOrStaff],
            "partial_update": [IsOwnerOrJobOwnerOrStaff],
            "destroy": [IsOwnerOrJobOwnerOrStaff],
            "bulk_create_skills": [IsOwnerOrJobOwnerOrStaffForCreate],
        },
        "UserSkillViewSet": {
            "list": [IsOwnerOrStaffForList],
            "retrieve": [IsOwnerOrStaffForList],
            "create": [permissions.IsAuthenticated],
            "update": [IsOwnerOrStaffForList],
            "partial_update": [IsOwnerOrStaffForList],
            "destroy": [IsOwnerOrStaffForList],
            "delete_skills": [permissions.IsAuthenticated],
            "get_job_recommendations": [permissions.IsAuthenticated],
            "get_skill_profile": [permissions.IsAuthenticated],
            "get_job_skill_match": [permissions.IsAuthenticated],
        },
    },
    "upload": {
        "UploadViewSet": {
            "list": [IsUploadOwnerOrStaff],
            "retrieve": [IsUploadOwnerOrStaff],
            "create": [permissions.IsAuthenticated],
            "update": [IsUploadOwnerOrStaff],
            "partial_update": [IsUploadOwnerOrStaff],
            "destroy": [IsUploadOwnerOrStaff],
        }
    },
    "address": {
        "AddressViewSet": {
            "list": [IsAddressOwnerOrStaff],
            "retrieve": [IsAddressOwnerOrStaff],
            "create": [permissions.IsAuthenticated],
            "update": [IsAddressOwnerOrStaff],
            "partial_update": [IsAddressOwnerOrStaff],
            "destroy": [IsAddressOwnerOrStaff],
        },
        "CityViewSet": {
            "list": [permissions.IsAuthenticated],
            "retrieve": [permissions.IsAuthenticated],
            "create": [IsAdminOnly],
            "update": [IsAdminOnly],
            "partial_update": [IsAdminOnly],
            "destroy": [IsAdminOnly],
        },
        "StateViewSet": {
            "list": [permissions.IsAuthenticated],
            "retrieve": [permissions.IsAuthenticated],
            "create": [IsAdminOnly],
            "update": [IsAdminOnly],
            "partial_update": [IsAdminOnly],
            "destroy": [IsAdminOnly],
        },
        "CountryViewSet": {
            "list": [permissions.IsAuthenticated],
            "retrieve": [permissions.IsAuthenticated],
            "create": [IsAdminOnly],
            "update": [IsAdminOnly],
            "partial_update": [IsAdminOnly],
            "destroy": [IsAdminOnly],
        },
    },
    "notification": {
        "NotificationListView": [permissions.IsAuthenticated],
        "NotificationUnreadCountView": [permissions.IsAuthenticated],
        "NotificationMarkReadView": [permissions.IsAuthenticated],
        "NotificationPreferenceView": [permissions.IsAuthenticated],
    },
    "feed": {
        "FeedListView": [permissions.IsAuthenticated],  # Changed from AllowAny
    },
    "promotion": {
        "PromotionPackageViewSet": {
            "list": [permissions.AllowAny],
            "retrieve": [permissions.AllowAny],
        },
        "PromotionViewSet": {
            "list": [permissions.IsAuthenticated],
            "retrieve": [permissions.IsAuthenticated],
            "create": [permissions.IsAuthenticated],
            "update": [IsOwnerOrStaff],
            "partial_update": [IsOwnerOrStaff],
            "destroy": [IsOwnerOrStaff],
            "activate": [IsAdminOnly],
            "cancel": [IsOwnerOrStaff],
        },
    },
}


def get_permissions_for_view(app_name, viewset_name, action=None):
    """
    Get permissions for a specific viewset and action.

    Args:
        app_name: Name of the app (e.g., 'user', 'job')
        viewset_name: Name of the viewset (e.g., 'UserViewSet')
        action: Specific action (e.g., 'list', 'create', 'retrieve')

    Returns:
        List of permission classes
    """
    if app_name not in PERMISSION_CONFIG:
        return [permissions.IsAuthenticated]

    app_config = PERMISSION_CONFIG[app_name]

    if viewset_name not in app_config:
        return [permissions.IsAuthenticated]

    viewset_config = app_config[viewset_name]

    # If action is specified, return action-specific permissions
    if action and action in viewset_config:
        return viewset_config[action]

    # If no action specified, return default permissions
    if isinstance(viewset_config, dict):
        # Return the most restrictive permission that applies to all actions
        if "list" in viewset_config:
            return viewset_config["list"]
        elif "create" in viewset_config:
            return viewset_config["create"]
        else:
            return [permissions.IsAuthenticated]

    # If viewset_config is a list, return it directly
    return viewset_config


def get_permission_classes_for_viewset(app_name, viewset_name):
    """
    Get permission classes for a viewset (for use in get_permissions method).

    Args:
        app_name: Name of the app
        viewset_name: Name of the viewset

    Returns:
        Dict mapping actions to permission classes
    """
    if app_name not in PERMISSION_CONFIG:
        return {"default": [permissions.IsAuthenticated]}

    app_config = PERMISSION_CONFIG[app_name]

    if viewset_name not in app_config:
        return {"default": [permissions.IsAuthenticated]}

    viewset_config = app_config[viewset_name]

    if isinstance(viewset_config, dict):
        return viewset_config
    else:
        return {"default": viewset_config}
