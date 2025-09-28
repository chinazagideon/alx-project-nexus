"""
Admin-only views for user management
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.pagination import DefaultPagination
from core.permissions import IsAdminOnly

from .admin_serializers import AdminUserCreateSerializer, AdminUserSerializer
from .models.models import User


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for user management including admin role assignment
    """

    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminOnly]
    pagination_class = DefaultPagination
    filterset_fields = ("role", "status", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    ordering_fields = ("created_at", "updated_at", "username", "email")
    ordering = ("-created_at",)

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == "create":
            return AdminUserCreateSerializer
        return AdminUserSerializer

    @extend_schema(
        operation_id="admin_user_create",
        summary="Create user (Admin only)",
        description="Create a new user with any role including admin (admin only)",
        tags=["Admin"],
        request=AdminUserCreateSerializer,
        responses={
            201: AdminUserSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new user (admin can assign any role)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_serializer = AdminUserSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="admin_user_list",
        summary="List all users (Admin only)",
        description="Get all users in the system (admin only)",
        tags=["Admin"],
        responses={200: AdminUserSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """
        List all users (admin only)
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        operation_id="admin_user_retrieve",
        summary="Get user details (Admin only)",
        description="Get detailed information about a specific user (admin only)",
        tags=["Admin"],
        responses={200: AdminUserSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Get user details (admin only)
        """
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        operation_id="admin_user_update",
        summary="Update user (Admin only)",
        description="Update user information including role assignment (admin only)",
        tags=["Admin"],
        request=AdminUserSerializer,
        responses={200: AdminUserSerializer, 400: OpenApiTypes.OBJECT},
    )
    def update(self, request, *args, **kwargs):
        """
        Update user (admin only)
        """
        return super().update(request, *args, **kwargs)

    @extend_schema(
        operation_id="admin_user_partial_update",
        summary="Partially update user (Admin only)",
        description="Partially update user information including role assignment (admin only)",
        tags=["Admin"],
        request=AdminUserSerializer,
        responses={200: AdminUserSerializer, 400: OpenApiTypes.OBJECT},
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update user (admin only)
        """
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        operation_id="admin_user_destroy",
        summary="Delete user (Admin only)",
        description="Delete a user from the system (admin only)",
        tags=["Admin"],
        responses={204: OpenApiTypes.OBJECT},
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete user (admin only)
        """
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        operation_id="admin_user_assign_admin_role",
        summary="Assign admin role to user",
        description="Assign admin role to a specific user (admin only)",
        tags=["Admin"],
        request={"type": "object", "properties": {"role": {"type": "string", "enum": ["admin", "recruiter", "talent"]}}},
        responses={200: AdminUserSerializer, 400: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=["patch"], url_path="assign-role")
    def assign_role(self, request, pk=None):
        """
        Assign a specific role to a user
        """
        user = self.get_object()
        new_role = request.data.get("role")

        if not new_role:
            return Response({"error": "Role is required"}, status=status.HTTP_400_BAD_REQUEST)

        if new_role not in ["admin", "recruiter", "talent"]:
            return Response(
                {"error": "Invalid role. Must be 'admin', 'recruiter', or 'talent'"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.role = new_role
        user.save()

        serializer = AdminUserSerializer(user)
        return Response(serializer.data)

    @extend_schema(
        operation_id="admin_user_toggle_status",
        summary="Toggle user status",
        description="Toggle user active/inactive status (admin only)",
        tags=["Admin"],
        responses={200: AdminUserSerializer, 400: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=["patch"], url_path="toggle-status")
    def toggle_status(self, request, pk=None):
        """
        Toggle user active/inactive status
        """
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()

        serializer = AdminUserSerializer(user)
        return Response(serializer.data)
