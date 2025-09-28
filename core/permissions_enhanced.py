"""
Enhanced permission classes for the application
"""

from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class BasePermissionMixin:
    """
    Base mixin for common permission logic
    """

    def is_owner(self, request, obj):
        """Check if user is the owner of the object"""
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        if hasattr(obj, "created_by"):
            return obj.created_by == request.user
        return False

    def is_staff_or_superuser(self, request):
        """Check if user is staff or superuser"""
        return request.user.is_staff or request.user.is_superuser


class IsOwnerOrReadOnly(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return self.is_owner(request, obj)


class IsOwnerOrStaff(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission to only allow owners or staff to access the object.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if self.is_staff_or_superuser(request):
            return True

        # Owners can access their own objects
        return self.is_owner(request, obj)


class IsOwnerOrStaffOrReadOnly(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission to allow owners/staff to edit, others to read.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Staff can edit everything
        if self.is_staff_or_superuser(request):
            return True

        # Owners can edit their own objects
        return self.is_owner(request, obj)


class IsOwnerOrStaffForList(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for list views - staff see all, others see only their own.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Staff can see everything
        if self.is_staff_or_superuser(request):
            return True

        # Users can only see their own objects
        return self.is_owner(request, obj)


class PublicReadAuthenticatedWrite(permissions.BasePermission):
    """
    Custom permission that allows public read access but requires authentication for write operations.
    """

    def has_permission(self, request, view):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Require authentication for write operations
        return request.user.is_authenticated


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission that allows read access to everyone but write access only to admin users.
    """

    def has_permission(self, request, view):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Require admin access for write operations
        return request.user.is_authenticated and request.user.is_staff


class IsAdminOnly(permissions.BasePermission):
    """
    Custom permission that allows access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsRecruiterOrAdmin(permissions.BasePermission):
    """
    Custom permission for recruiter or admin access.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.role in ["recruiter", "admin"] or request.user.is_staff


class IsTalentOrAdmin(permissions.BasePermission):
    """
    Custom permission for talent or admin access.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.role in ["talent", "admin"] or request.user.is_staff


class IsJobOwnerOrStaff(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for job-related operations.
    Checks if user owns the job (through company) or is staff.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if self.is_staff_or_superuser(request):
            return True

        # Check if user owns the job through company
        if hasattr(obj, "company") and hasattr(obj.company, "user"):
            return obj.company.user == request.user

        # Check if user is the direct owner
        return self.is_owner(request, obj)


class IsCompanyOwnerOrStaff(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for company-related operations.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if self.is_staff_or_superuser(request):
            return True

        # Check if user owns the company
        return self.is_owner(request, obj)


class IsApplicationOwnerOrJobOwnerOrStaff(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for application-related operations.
    Allows access to:
    - Application owner (talent who applied)
    - Job owner (recruiter who posted the job)
    - Staff/Admin
    """

    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if self.is_staff_or_superuser(request):
            return True

        # Application owner can access
        if hasattr(obj, "user") and obj.user == request.user:
            return True

        # Job owner can access (through company)
        if hasattr(obj, "job") and hasattr(obj.job, "company"):
            if hasattr(obj.job.company, "user") and obj.job.company.user == request.user:
                return True

        return False


class IsUploadOwnerOrStaff(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for upload-related operations.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if self.is_staff_or_superuser(request):
            return True

        # Check if user owns the upload
        if hasattr(obj, "uploaded_by"):
            return obj.uploaded_by == request.user

        return self.is_owner(request, obj)


class IsAddressOwnerOrStaff(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for address-related operations.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if self.is_staff_or_superuser(request):
            return True

        # Check if user owns the address
        return self.is_owner(request, obj)


class RoleBasedPermission(permissions.BasePermission):
    """
    Generic role-based permission class.
    """

    def __init__(self, allowed_roles=None, allow_staff=True):
        self.allowed_roles = allowed_roles or []
        self.allow_staff = allow_staff

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Staff can access if allowed
        if self.allow_staff and (request.user.is_staff or request.user.is_superuser):
            return True

        # Check if user role is allowed
        return request.user.role in self.allowed_roles


class IsOwnerOrJobOwnerOrStaff(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for job-skill associations.
    Allows access to:
    - Job owner (through company)
    - Staff/Admin
    """

    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if self.is_staff_or_superuser(request):
            return True

        # Check if user owns the job through company
        if hasattr(obj, "job") and hasattr(obj.job, "company"):
            if hasattr(obj.job.company, "user") and obj.job.company.user == request.user:
                return True

        return False


class IsOwnerOrJobOwnerOrStaffForCreate(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for creating job-skill associations.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Staff can create anything
        if self.is_staff_or_superuser(request):
            return True

        # For job-skill associations, check if user owns the job
        if view.action == "create":
            job_id = request.data.get("job")
            if job_id:
                from job.models import Job

                try:
                    job = Job.objects.get(id=job_id)
                    if hasattr(job, "company") and hasattr(job.company, "user"):
                        return job.company.user == request.user
                except Job.DoesNotExist:
                    return False

        return True
