from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification, NotificationPreference, NotificationStatus
from .serializers import NotificationPreferenceSerializer, NotificationSerializer
from .services import decr_unread, get_unread


class NotificationListView(APIView):
    """
    Viewset for the notification list
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: NotificationSerializer(many=True)})
    def get(self, request):
        """
        Get the notification list
        """
        qs = Notification.objects.filter(user=request.user).order_by("-created_at", "-id")
        status_filter = request.query_params.get("status")
        if status_filter == "unread":
            qs = qs.exclude(status=NotificationStatus.READ)
        page_size = int(request.query_params.get("page_size", 20))
        page = int(request.query_params.get("page", 1))
        start = (page - 1) * page_size
        end = start + page_size
        items = list(qs[start:end])
        return Response(
            {
                "results": NotificationSerializer(items, many=True).data,
                "page": page,
                "page_size": page_size,
            }
        )


class NotificationUnreadCountView(APIView):
    """
    Viewset for the notification unread count
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: {"type": "object", "properties": {"count": {"type": "integer"}}}})
    def get(self, request):
        return Response({"count": get_unread(request.user.id)})


class NotificationMarkReadView(APIView):
    """
    Notification mark read view
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={"type": "object", "properties": {"ids": {"type": "array", "items": {"type": "integer"}}}},
        responses={200: {"type": "object"}},
        operation_id="notification_mark_read",
        summary="Mark notifications as read",
        tags=["notifications"],
    )
    def post(self, request):
        """
        Mark the notification as read
        """
        ids = request.data.get("ids", [])
        if not isinstance(ids, list):
            return Response({"detail": "ids must be a list"}, status=status.HTTP_400_BAD_REQUEST)
        qs = Notification.objects.filter(user=request.user, id__in=ids).exclude(status=NotificationStatus.READ)
        count = qs.count()
        for n in qs:
            n.mark_read()
        if count:
            decr_unread(request.user.id, count)
        return Response({"updated": count})


class NotificationPreferenceView(APIView):
    """
    Viewset for the notification preference
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: NotificationPreferenceSerializer})
    def get(self, request):
        """
        Get the notification preference
        """
        pref, _ = NotificationPreference.objects.get_or_create(user=request.user)
        return Response(NotificationPreferenceSerializer(pref).data)

    @extend_schema(request=NotificationPreferenceSerializer, responses={200: NotificationPreferenceSerializer})
    def put(self, request):
        """
        Update the notification preference
        """
        pref, _ = NotificationPreference.objects.get_or_create(user=request.user)
        ser = NotificationPreferenceSerializer(pref, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)
