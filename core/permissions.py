"""
Custom permission classes for the application
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners or staff to access the object.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if request.user.is_staff:
            return True

        # Owners can access their own objects
        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


class IsOwnerOrStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow owners/staff to edit, others to read.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Staff can edit everything
        if request.user.is_staff:
            return True

        # Owners can edit their own objects
        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


class IsOwnerOrStaffForList(permissions.BasePermission):
    """
    Custom permission for list views - staff see all, others see only their own.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Staff can see everything
        if request.user.is_staff:
            return True

        # Users can only see their own objects
        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


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
