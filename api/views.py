from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework import serializers
from core.response import APIResponse, create_success_response_serializer, create_error_response_serializer
from core.mixins import StandardAPIViewMixin
from drf_spectacular.utils import extend_schema, extend_schema_view
from user.serializers import UserSerializer


class LoginResponseSerializer(serializers.Serializer):
    """
    Serializer for login response that includes tokens and user data
    """
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    user = UserSerializer(help_text="User profile data")


class ProtectedView(StandardAPIViewMixin, APIView):
    """
    Protected view
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='protected_view_get',
        summary='Get protected data',
        description='Access protected data that requires authentication',
        tags=['Auth'],
        responses={
            200: create_success_response_serializer(
                data_serializer=serializers.DictField(),
                message="Protected data retrieved successfully"
            ),
            401: create_error_response_serializer(
                message="Authentication required",
                status_code=401
            ),
        }
    )
    def get(self, request):
        """
        Get the protected view
        """
        return self.success_response(
            data={"message": "This is a protected view"},
            message="Protected data retrieved successfully"
        )


class LogoutAllView(StandardAPIViewMixin, APIView):
    """
    View to logout all devices for the user
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='auth_logout_all', 
        summary='Logout from all devices', 
        tags=['Auth'],
        responses={
            200: create_success_response_serializer(
                data_serializer=serializers.JSONField(allow_null=True),
                message="Logged out from all devices successfully"
            ),
            401: create_error_response_serializer(
                message="Authentication required",
                status_code=401
            ),
        }
    )
    def post(self, request):
        """
        Logout all devices for the user
        """
        tokens = OutstandingToken.objects.filter(user=request.user)
        for t in tokens:
            BlacklistedToken.objects.get_or_create(token=t)
        return self.success_response(
            data=None,
            message="Logged out from all devices successfully"
        )


@extend_schema_view(
    post=extend_schema(
        operation_id='auth_login', 
        summary='Login (obtain access & refresh)', 
        tags=['Auth'],
        responses={
            200: create_success_response_serializer(
                data_serializer=LoginResponseSerializer(),
                message="Login successful"
            ),
            401: create_error_response_serializer(
                message="Invalid credentials",
                status_code=401
            ),
        }
    )
)
class LoginView(TokenObtainPairView):
    """
    Custom login view that returns user data along with JWT tokens
    """
    
    def post(self, request, *args, **kwargs):
        """
        Override post method to include user data in response
        """
        # Get the original response from TokenObtainPairView
        response = super().post(request, *args, **kwargs)
        
        # Check if login was successful (status 200)
        if response.status_code == 200:
            # Get the user from the serializer's validated data
            # The TokenObtainPairView sets the user in the serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            
            # Serialize user data
            user_serializer = UserSerializer(user)
            
            # Create new response data with user information
            response_data = response.data.copy()
            response_data['user'] = user_serializer.data
            
            # Return standardized API response
            return APIResponse.success(
                data=response_data,
                message="Login successful"
            )
        
        # For error responses, return as is
        return response


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
        