from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserSerializer, UserRegistrationSerializer
from .models.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.pagination import DefaultPagination
from core.permissions import IsOwnerOrStaffForList, IsAdminOnly
from core.response import APIResponse, SuccessResponseSerializer, ErrorResponseSerializer, ValidationErrorResponseSerializer
from core.mixins import StandardResponseMixin
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes


class UserViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    """
    User viewset for both public registration and authenticated operations
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = DefaultPagination
    filterset_fields = ('role', 'status')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            # Allow public registration
            permission_classes = [AllowAny]
        elif self.action == 'list':
            # Only admin can list all users
            permission_classes = [IsAdminOnly]
        else:
            # Require authentication for other operations
            permission_classes = [IsOwnerOrStaffForList]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Get the queryset for the user list
        """
        if self.action == 'list':
            # Only show current user's profile for non-staff users
            if not self.request.user.is_staff:
                return User.objects.filter(id=self.request.user.id)
        return super().get_queryset()

    @extend_schema(
        operation_id="user_register",
        summary="Register new user",
        description="Create a new user account ",
        tags=["Auth"],
        request=UserRegistrationSerializer,
        responses={
            201: SuccessResponseSerializer,
            400: ValidationErrorResponseSerializer,
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Register new user account
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Return user data without password
        response_serializer = UserSerializer(user)
        return APIResponse.created(
            data=response_serializer.data,
            message="User registered successfully"
        )

    @extend_schema(
        operation_id="user_profile_get",
        summary="Get current user profile",
        description="Get the current authenticated user's profile",
        tags=["users"],
        responses={
            200: SuccessResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        """
        Get current user's profile
        """
        serializer = self.get_serializer(request.user)
        return APIResponse.success(
            data=serializer.data,
            message="User profile retrieved successfully"
        )

    @extend_schema(
        operation_id="user_profile_update_put",
        summary="Update current user profile (PUT)",
        description="Update the current authenticated user's profile (full update)",
        tags=["users"],
        request=UserSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    @action(detail=False, methods=['put'], url_path='profile')
    def update_profile_put(self, request):
        """
        Update current user's profile (full update)
        """
        serializer = self.get_serializer(request.user, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(
            data=serializer.data,
            message="User profile updated successfully"
        )

    @extend_schema(
        operation_id="user_profile_update_patch",
        summary="Update current user profile (PATCH)",
        description="Update the current authenticated user's profile (partial update)",
        tags=["users"],
        request=UserSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    @action(detail=False, methods=['patch'], url_path='profile')
    def update_profile_patch(self, request):
        """
        Update current user's profile (partial update)
        """
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(
            data=serializer.data,
            message="User profile updated successfully"
        )
    
    @extend_schema(
        # exclude=True,
        summary="List users",
        description="List users (admin only)",
        tags=["users"],
        responses={
            200: SuccessResponseSerializer,
            403: ErrorResponseSerializer,
        },
    )
    def list(self, request, *args, **kwargs):
        """
        List users (admin only)
        """
        return super().list(request, *args, **kwargs)