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

    def is_email_verified(self, request):
        """Check if user's email is verified"""
        return request.user.is_authenticated and request.user.is_email_verified

    def requires_email_verification(self, request):
        """
        Check if email verification is required for the current request.
        Email verification is required for all actions except:
        - Login/logout
        - Email verification endpoints
        - Public read access (if applicable)
        """
        # Allow unauthenticated users to pass through (handled by other permissions)
        if not request.user.is_authenticated:
            return True

        # Staff and superusers are exempt from email verification requirement
        if self.is_staff_or_superuser(request):
            return True

        # Check if user is active (email verified and status is active)
        return request.user.status == "active"


class IsOwnerOrReadOnly(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission to only allow owners of an object to edit it.
    Requires email verification for write operations.
    """

    def has_permission(self, request, view):
        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False
        return True

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
    Requires email verification for non-staff users.
    """

    def has_permission(self, request, view):
        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if self.is_staff_or_superuser(request):
            return True

        # Owners can access their own objects
        return self.is_owner(request, obj)


class IsOwnerOrStaffOrReadOnly(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission to allow owners/staff to edit, others to read.
    Requires email verification for write operations.
    """

    def has_permission(self, request, view):
        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False
        return True

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
    Requires email verification for non-staff users.
    """

    def has_permission(self, request, view):
        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # Staff can see everything
        if self.is_staff_or_superuser(request):
            return True

        # Users can only see their own objects
        return self.is_owner(request, obj)


class PublicReadAuthenticatedWrite(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission that allows public read access but requires authentication and email verification for write operations.
    """

    def has_permission(self, request, view):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Require authentication and email verification for write operations
        return request.user.is_authenticated and self.requires_email_verification(request)


class IsAdminOrReadOnly(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission that allows read access to everyone but write access only to admin users.
    """

    def has_permission(self, request, view):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Require admin access for write operations (staff are exempt from email verification)
        return request.user.is_authenticated and request.user.is_staff


class IsAdminOnly(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission that allows access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsRecruiterOrAdmin(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for recruiter or admin access.
    Requires email verification for non-staff users.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False

        return request.user.role in ["recruiter", "admin"] or request.user.is_staff


class IsTalentOrAdmin(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for talent or admin access.
    Requires email verification for non-staff users.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False

        return request.user.role in ["talent", "admin"] or request.user.is_staff


class IsJobOwnerOrStaff(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for job-related operations.
    Checks if user owns the job (through company) or is staff.
    Requires email verification for non-staff users.
    """

    def has_permission(self, request, view):
        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False
        return True

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
    Requires email verification for non-staff users.
    """

    def has_permission(self, request, view):
        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False
        return True

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
    Requires email verification for non-staff users.
    """

    def has_permission(self, request, view):
        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False
        return True

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
    Requires email verification for non-staff users.
    """

    def has_permission(self, request, view):
        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False
        return True

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
    Requires email verification for non-staff users.
    """

    def has_permission(self, request, view):
        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if self.is_staff_or_superuser(request):
            return True

        # Check if user owns the address
        return self.is_owner(request, obj)


class RoleBasedPermission(permissions.BasePermission, BasePermissionMixin):
    """
    Generic role-based permission class.
    Requires email verification for non-staff users.
    """

    def __init__(self, allowed_roles=None, allow_staff=True):
        self.allowed_roles = allowed_roles or []
        self.allow_staff = allow_staff

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check email verification requirement first
        if not self.requires_email_verification(request):
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
    Requires email verification for non-staff users.
    """

    def has_permission(self, request, view):
        # Check email verification requirement first
        if not self.requires_email_verification(request):
            return False
        return True

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
    Requires email verification for non-staff users.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check email verification requirement first
        if not self.requires_email_verification(request):
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


class IsAccountActive(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission for account active.
    Requires user to be active (status=active) for non-staff users.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check email verification requirement first (now checks status)
        if not self.requires_email_verification(request):
            return False

        return request.user.is_active


class IsAuthenticatedNoEmailVerification(permissions.BasePermission):
    """
    Custom permission that only requires authentication, no email verification.
    Used for login, logout, and email verification endpoints.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated


class AllowAnyNoEmailVerification(permissions.BasePermission):
    """
    Custom permission that allows any access, no authentication or email verification required.
    Used for public endpoints like registration, email verification, etc.
    """

    def has_permission(self, request, view):
        return True


class IsAuthenticatedWithEmailVerification(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission that requires both authentication and email verification.
    This is the default for most authenticated endpoints.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check email verification requirement
        return self.requires_email_verification(request)


class IsActiveUser(permissions.BasePermission, BasePermissionMixin):
    """
    Custom permission that requires user to be active (status=active).
    This replaces the old email verification checks.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Staff and superusers are exempt
        if self.is_staff_or_superuser(request):
            return True

        # Check if user is active
        return request.user.status == "active"
