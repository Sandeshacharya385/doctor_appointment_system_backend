from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
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
