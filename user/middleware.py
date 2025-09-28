"""
Middleware for user authentication
"""

from rest_framework import status
from rest_framework.response import Response


class MFAMiddleware:
    """
    Middleware for user authentication
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Call the middleware
        """
        if request.user.is_authenticated:
            if request.user.mfa_enabled:
                if not request.user.mfa_verified:
                    return Response({"error": "MFA not verified"}, status=status.HTTP_401_UNAUTHORIZED)
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process the view
        """
        return self.get_response(request)
