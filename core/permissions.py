from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Permission to check if the user is an admin
    """
    def has_permission(self, request, view):
        user = request.user
        """
        Check if the user is an admin
        """
        return user.is_authenticated and getattr(user, 'role', None) == 'admin'

class IsRecruiter(BasePermission):
    """
    Permission to check if the user is a recruiter
    """
    def has_permission(self, request, view):
        user = request.user
        """
        Check if the user is a recruiter
        """
        return user.is_authenticated and getattr(user, 'role', None) == 'recruiter'

class IsTalent(BasePermission):
    """
    Permission to check if the user is a talent
    """
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and getattr(user, 'role', None) == 'talent'