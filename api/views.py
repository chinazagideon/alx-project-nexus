from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from drf_spectacular.utils import extend_schema, extend_schema_view


class ProtectedView(APIView):
    """
    Protected view
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get the protected view
        """
        return Response({"message": "This is a protected view"})


class LogoutAllView(APIView):
    """
    View to logout all devices for the user
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='auth_logout_all', 
        summary='Logout from all devices', 
        tags=['Auth'],
        responses={200: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}}
    )
    def post(self, request):
        """
        Logout all devices for the user
        """
        tokens = OutstandingToken.objects.filter(user=request.user)
        for t in tokens:
            BlacklistedToken.objects.get_or_create(token=t)
        return Response({"detail": "Logged out from all devices"}, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(operation_id='auth_login', summary='Login (obtain access & refresh)', tags=['Auth'])
)
class LoginView(TokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(operation_id='auth_refresh', summary='Refresh access token', tags=['Auth'])
)
class RefreshView(TokenRefreshView):
    pass


@extend_schema_view(
    post=extend_schema(operation_id='auth_logout', summary='Logout (blacklist refresh token)', tags=['Auth'])
)
class LogoutView(TokenBlacklistView):
    pass
        