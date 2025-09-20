from django.utils import timezone
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Promotion, PromotionPackage, PromotionStatus
from .serializers import PromotionSerializer, PromotionPackageSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class for the promotion model
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.user and (request.user.is_staff or obj.owner_id == request.user.id))


class PromotionPackageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    View for listing promotion packages
    """
    queryset = PromotionPackage.objects.filter(is_active=True)
    serializer_class = PromotionPackageSerializer
    permission_classes = [permissions.AllowAny]


class PromotionViewSet(viewsets.ModelViewSet):
    """
    View for listing promotions
    """
    queryset = Promotion.objects.all().select_related("package", "owner")
    serializer_class = PromotionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """
        Get the queryset for the promotion list
        """
        qs = super().get_queryset()
        # only allow owners to see their promotions unless staff
        if not self.request.user.is_staff:
            qs = qs.filter(owner=self.request.user)
        # optional filters
        status_param = self.request.query_params.get("status")
        type_param = self.request.query_params.get("type")
        if status_param:
            qs = qs.filter(status=status_param)
        if type_param:
            qs = qs.filter(type=type_param)
        return qs

    def perform_create(self, serializer):
        """
        Perform the create action for the promotion
        """
        instance = serializer.save()
        # If you need payment confirmation, keep as pending; else auto-activate
        instance.activate(when=instance.start_at)

    @extend_schema(operation_id="promotions_activate_create")
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def activate(self, request, pk=None):
        """
        Activate the promotion
        """
        promotion = self.get_object()
        promotion.activate(when=promotion.start_at or timezone.now())
        return Response(self.get_serializer(promotion).data)

    @extend_schema(operation_id="promotions_cancel_create")
    @action(detail=True, methods=["post"], permission_classes=[IsOwnerOrAdmin])

    def cancel(self, request, pk=None):
        """
        Cancel the promotion
        """
        promotion = self.get_object()
        promotion.status = PromotionStatus.CANCELLED
        promotion.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(promotion).data, status=status.HTTP_200_OK)

