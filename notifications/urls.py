from django.urls import path
from .views import (
    NotificationListView, 
    MarkNotificationReadView, 
    MarkAllNotificationsReadView,
    CreateTestNotificationView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='notification-mark-read'),
    path('mark-all-read/', MarkAllNotificationsReadView.as_view(), name='notification-mark-all-read'),
    path('test/', CreateTestNotificationView.as_view(), name='notification-test'),
]
