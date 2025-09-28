"""
Permission mixins for viewsets to easily apply proper permissions.
"""

from rest_framework import permissions
from core.permission_config import get_permission_classes_for_viewset


class PermissionConfigMixin:
    """
    Mixin that automatically applies permissions based on configuration.

    Usage:
        class MyViewSet(PermissionConfigMixin, viewsets.ModelViewSet):
            app_name = 'my_app'
            viewset_name = 'MyViewSet'
    """

    app_name = None
    viewset_name = None

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if not self.app_name or not self.viewset_name:
            # Fallback to default permissions
            return [permissions.IsAuthenticated()]

        permission_config = get_permission_classes_for_viewset(self.app_name, self.viewset_name)

        # Get permissions for the current action
        action = self.action
        if action in permission_config:
            permission_classes = permission_config[action]
        elif "default" in permission_config:
            permission_classes = permission_config["default"]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


class JobPermissionMixin:
    """
    Mixin for job-related viewsets that need job ownership checks.
    """

    def get_permissions(self):
        """
        Apply job-specific permissions.
        """
        from core.permissions_enhanced import (
            IsRecruiterOrAdmin,
            IsJobOwnerOrStaff,
            IsOwnerOrJobOwnerOrStaffForCreate,
            IsOwnerOrJobOwnerOrStaff,
        )

        if self.action == "create":
            permission_classes = [IsRecruiterOrAdmin]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsJobOwnerOrStaff]
        elif self.action == "list":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


class ApplicationPermissionMixin:
    """
    Mixin for application-related viewsets.
    """

    def get_permissions(self):
        """
        Apply application-specific permissions.
        """
        from core.permissions_enhanced import IsTalentOrAdmin, IsApplicationOwnerOrJobOwnerOrStaff

        if self.action == "create":
            permission_classes = [IsTalentOrAdmin]
        elif self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
            permission_classes = [IsApplicationOwnerOrJobOwnerOrStaff]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


class CompanyPermissionMixin:
    """
    Mixin for company-related viewsets.
    """

    def get_permissions(self):
        """
        Apply company-specific permissions.
        """
        from core.permissions_enhanced import IsRecruiterOrAdmin, IsCompanyOwnerOrStaff

        if self.action == "create":
            permission_classes = [IsRecruiterOrAdmin]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsCompanyOwnerOrStaff]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


class SkillPermissionMixin:
    """
    Mixin for skill-related viewsets.
    """

    def get_permissions(self):
        """
        Apply skill-specific permissions.
        """
        from core.permissions_enhanced import (
            IsAdminOnly,
            IsOwnerOrJobOwnerOrStaffForCreate,
            IsOwnerOrJobOwnerOrStaff,
            IsOwnerOrStaffForList,
            PublicReadAuthenticatedWrite,
        )

        if self.action in ["create", "update", "partial_update", "destroy"]:
            if "JobSkill" in self.__class__.__name__:
                if self.action == "create":
                    permission_classes = [IsOwnerOrJobOwnerOrStaffForCreate]
                else:
                    permission_classes = [IsOwnerOrJobOwnerOrStaff]
            elif "UserSkill" in self.__class__.__name__:
                permission_classes = [IsOwnerOrStaffForList]
            else:  # SkillViewSet
                permission_classes = [IsAdminOnly]
        elif self.action in ["list", "retrieve"]:
            if (
                "Skill" in self.__class__.__name__
                and "Job" not in self.__class__.__name__
                and "User" not in self.__class__.__name__
            ):
                permission_classes = [PublicReadAuthenticatedWrite]
            else:
                permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


class UploadPermissionMixin:
    """
    Mixin for upload-related viewsets.
    """

    def get_permissions(self):
        """
        Apply upload-specific permissions.
        """
        from core.permissions_enhanced import IsUploadOwnerOrStaff

        if self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
            permission_classes = [IsUploadOwnerOrStaff]
        elif self.action == "create":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


class AddressPermissionMixin:
    """
    Mixin for address-related viewsets.
    """

    def get_permissions(self):
        """
        Apply address-specific permissions.
        """
        from core.permissions_enhanced import IsAddressOwnerOrStaff, IsAdminOnly

        if "Address" in self.__class__.__name__:
            if self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
                permission_classes = [IsAddressOwnerOrStaff]
            elif self.action == "create":
                permission_classes = [permissions.IsAuthenticated]
            else:
                permission_classes = [permissions.IsAuthenticated]
        else:  # City, State, Country
            if self.action in ["create", "update", "partial_update", "destroy"]:
                permission_classes = [IsAdminOnly]
            else:
                permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]
