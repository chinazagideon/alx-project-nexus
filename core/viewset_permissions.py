"""
Specific fixes for viewsets with critical permission issues.
These can be directly applied to fix the most urgent security vulnerabilities.
"""

from rest_framework import permissions

from core.permissions_enhanced import (
    IsAddressOwnerOrStaff,
    IsAdminOnly,
    IsCompanyOwnerOrStaff,
    IsJobOwnerOrStaff,
    IsOwnerOrJobOwnerOrStaff,
    IsOwnerOrJobOwnerOrStaffForCreate,
    IsRecruiterOrAdmin,
    IsUploadOwnerOrStaff,
)


def get_job_permissions(self):
    """
    Permission method for JobViewSet and JobListCreateView
    """
    if self.action == "create":
        permission_classes = [IsRecruiterOrAdmin]
    elif self.action in ["update", "partial_update", "destroy"]:
        permission_classes = [IsJobOwnerOrStaff]
    else:
        permission_classes = [permissions.IsAuthenticated]
    return [permission() for permission in permission_classes]


def get_company_permissions(self):
    """
    Permission method for CompanyViewSet
    """
    if self.action == "create":
        permission_classes = [IsRecruiterOrAdmin]
    elif self.action in ["update", "partial_update", "destroy"]:
        permission_classes = [IsCompanyOwnerOrStaff]
    else:
        permission_classes = [permissions.IsAuthenticated]
    return [permission() for permission in permission_classes]


def get_upload_permissions(self):
    """
    Permission method for UploadViewSet
    """
    if self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
        permission_classes = [IsUploadOwnerOrStaff]
    elif self.action == "create":
        permission_classes = [permissions.IsAuthenticated]
    else:
        permission_classes = [permissions.IsAuthenticated]
    return [permission() for permission in permission_classes]


def get_address_permissions(self):
    """
    Permission method for AddressViewSet
    """
    if self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
        permission_classes = [IsAddressOwnerOrStaff]
    elif self.action == "create":
        permission_classes = [permissions.IsAuthenticated]
    else:
        permission_classes = [permissions.IsAuthenticated]
    return [permission() for permission in permission_classes]


def get_job_skill_permissions(self):
    """
    Permission method for JobSkillViewSet
    """
    if self.action == "create":
        permission_classes = [IsOwnerOrJobOwnerOrStaffForCreate]
    elif self.action in ["update", "partial_update", "destroy"]:
        permission_classes = [IsOwnerOrJobOwnerOrStaff]
    else:
        permission_classes = [permissions.IsAuthenticated]
    return [permission() for permission in permission_classes]


def get_city_state_country_permissions(self):
    """
    Permission method for CityViewSet, StateViewSet, CountryViewSet
    """
    if self.action in ["create", "update", "partial_update", "destroy"]:
        permission_classes = [IsAdminOnly]
    else:
        permission_classes = [permissions.IsAuthenticated]
    return [permission() for permission in permission_classes]


# Queryset filtering methods
def get_job_queryset(self):
    """
    Queryset method for JobViewSet and JobListCreateView
    """
    if self.request.user.is_staff:
        return self.queryset
    elif self.request.user.role == "recruiter":
        return self.queryset.filter(company__user=self.request.user)
    else:
        return self.queryset  # Talent can see all jobs


def get_company_queryset(self):
    """
    Queryset method for CompanyViewSet
    """
    if self.request.user.is_staff:
        return self.queryset
    else:
        return self.queryset.filter(user=self.request.user)


def get_upload_queryset(self):
    """
    Queryset method for UploadViewSet
    """
    if self.request.user.is_staff:
        return self.queryset
    else:
        return self.queryset.filter(uploaded_by=self.request.user)


def get_address_queryset(self):
    """
    Queryset method for AddressViewSet
    """
    if self.request.user.is_staff:
        return self.queryset
    else:
        return self.queryset.filter(user=self.request.user)


def get_job_skill_queryset(self):
    """
    Queryset method for JobSkillViewSet
    """
    if self.request.user.is_staff:
        return self.queryset
    elif self.request.user.role == "recruiter":
        return self.queryset.filter(job__company__user=self.request.user)
    else:
        return self.queryset  # Talent can see all job skills for job search
