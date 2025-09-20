from django.shortcuts import render
from rest_framework import viewsets
from .serializers import UserSerializer
from .models.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.pagination import DefaultPagination

class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for the user model
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filterset_fields = ('role', 'status')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    def get_queryset(self):
        """
        Get the queryset for the user list
        """
        return super().get_queryset()

