from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Notification
from .serializers import NotificationSerializer

@extend_schema_view(
    get=extend_schema(
        tags=['Notifications'],
        summary='List user notifications',
        description='Retrieve list of notifications for the authenticated user, ordered by most recent first.',
        responses={
            200: NotificationSerializer(many=True),
            401: OpenApiTypes.OBJECT,
        },
    )
)
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@extend_schema(
    tags=['Notifications'],
    summary='Mark notification as read',
    description='Mark a specific notification as read for the authenticated user.',
    parameters=[
        OpenApiParameter(
            name='pk',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Notification ID',
            required=True,
        ),
    ],
    responses={
        200: NotificationSerializer,
        404: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
    },
)
class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response(NotificationSerializer(notification).data)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=['Notifications'],
    summary='Mark all notifications as read',
    description='Mark all notifications as read for the authenticated user.',
    responses={
        200: {'type': 'object', 'properties': {'message': {'type': 'string'}}},
        401: OpenApiTypes.OBJECT,
    },
)
class MarkAllNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read'})
