from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView

from core.mixins import StandardAPIViewMixin
from core.response import APIResponse, create_error_response_serializer, create_success_response_serializer
from upload.serializers import UploadSerializer
from user.serializers import UserRegistrationSerializer, UserSerializer


class LoginResponseSerializer(serializers.Serializer):
    """
    Serializer for login response that includes tokens and user data
    """

    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    user = UserSerializer(help_text="User profile data")
    uploads = UploadSerializer(many=True, help_text="User uploads", required=False)


class ProtectedView(StandardAPIViewMixin, APIView):
    """
    Protected view
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="protected_view_get",
        summary="Get protected data",
        description="Access protected data that requires authentication",
        tags=["Auth"],
        responses={
            200: create_success_response_serializer(
                data_serializer=serializers.DictField(), message="Protected data retrieved successfully"
            ),
            401: create_error_response_serializer(message="Authentication required", status_code=401),
        },
    )
    def get(self, request):
        """
        Get the protected view
        """
        return self.success_response(
            data={"message": "This is a protected view"}, message="Protected data retrieved successfully"
        )


class LogoutAllView(StandardAPIViewMixin, APIView):
    """
    View to logout all devices for the user
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="auth_logout_all",
        summary="Logout from all devices",
        tags=["Auth"],
        responses={
            200: create_success_response_serializer(
                data_serializer=serializers.JSONField(allow_null=True), message="Logged out from all devices successfully"
            ),
            401: create_error_response_serializer(message="Authentication required", status_code=401),
        },
    )
    def post(self, request):
        """
        Logout all devices for the user
        """
        tokens = OutstandingToken.objects.filter(user=request.user)
        for t in tokens:
            BlacklistedToken.objects.get_or_create(token=t)
        return self.success_response(data=None, message="Logged out from all devices successfully")


@extend_schema_view(
    post=extend_schema(
        operation_id="auth_login",
        summary="Login (obtain access & refresh)",
        tags=["Auth"],
        responses={
            200: {
                "description": "Login successful",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "message": {"type": "string"},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "access": {"type": "string", "description": "JWT access token"},
                                        "refresh": {"type": "string", "description": "JWT refresh token"},
                                        "user": {
                                            "type": "object",
                                            "description": "User profile data",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "username": {"type": "string"},
                                                "email": {"type": "string"},
                                                "first_name": {"type": "string"},
                                                "last_name": {"type": "string"},
                                                "role": {"type": "string"},
                                                "is_email_verified": {"type": "boolean"},
                                            },
                                        },
                                        "uploads": {
                                            "type": "array",
                                            "description": "User uploads (if any)",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "name": {"type": "string"},
                                                    "type": {"type": "string"},
                                                    "file_url": {"type": "string"},
                                                    "file_size": {"type": "integer"},
                                                    "created_at": {"type": "string", "format": "date-time"},
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        }
                    }
                },
            },
            401: create_error_response_serializer(message="Invalid credentials", status_code=401),
        },
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

            # Get user uploads
            from upload.models import Upload

            user_uploads = Upload.objects.filter(uploaded_by=user).order_by("-created_at")
            uploads_serializer = UploadSerializer(user_uploads, many=True, context={"request": request})

            # Create new response data with user information and uploads
            response_data = response.data.copy()
            response_data["user"] = user_serializer.data
            response_data["uploads"] = uploads_serializer.data

            # Return standardized API response
            return APIResponse.success(data=response_data, message="Login successful")

        # For error responses, return as is
        return response


@extend_schema_view(post=extend_schema(operation_id="auth_refresh", summary="Refresh access token", tags=["Auth"]))
class RefreshView(TokenRefreshView):
    pass


@extend_schema_view(post=extend_schema(operation_id="auth_logout", summary="Logout (blacklist refresh token)", tags=["Auth"]))
class LogoutView(TokenBlacklistView):
    pass


class RegistrationView(StandardAPIViewMixin, APIView):
    """
    Public user registration view
    """

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="auth_register",
        summary="Register new user",
        description="Create a new user account (public endpoint)",
        tags=["Auth"],
        request=UserRegistrationSerializer,
        responses={
            201: create_success_response_serializer(data_serializer=UserSerializer(), message="User registered successfully"),
            400: create_error_response_serializer(message="Validation error", status_code=400),
        },
    )
    def post(self, request):
        """
        Register a new user account
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Send email verification asynchronously
        try:
            from notification.tasks import send_email_verification

            send_email_verification.delay(user.id)
        except Exception as e:
            # Log the error but don't fail registration
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to queue email verification for user {user.id}: {str(e)}")

        # Return user data without password
        response_serializer = UserSerializer(user)
        return self.success_response(
            data=response_serializer.data,
            message="User registered successfully. Please check your email to verify your account.",
            status_code=201,
        )
