from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        help_text='ID of the user who receives this notification'
    )
    title = serializers.CharField(
        max_length=200,
        help_text='Notification title or subject'
    )
    message = serializers.CharField(
        help_text='Notification message content'
    )
    is_read = serializers.BooleanField(
        default=False,
        help_text='Whether the notification has been read by the user'
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text='Timestamp when the notification was created'
    )
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['user', 'created_at']
