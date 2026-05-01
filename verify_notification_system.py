import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_appointment.settings')
django.setup()

from notifications.models import Notification
from users.models import User
from appointments.models import Appointment
from doctors.models import Doctor

print("=" * 60)
print("NOTIFICATION SYSTEM VERIFICATION")
print("=" * 60)

# Check if notifications exist
total_notifications = Notification.objects.count()
print(f"\n✓ Total notifications in database: {total_notifications}")

# Show recent notifications
print("\nRecent Notifications:")
print("-" * 60)
recent = Notification.objects.all()[:10]
for n in recent:
    status = "✓ Read" if n.is_read else "○ Unread"
    print(f"{status} | {n.user.username:15} | {n.title:30} | {n.created_at.strftime('%Y-%m-%d %H:%M')}")

# Check notification counts by user
print("\nNotifications by User:")
print("-" * 60)
from django.db.models import Count
user_counts = Notification.objects.values('user__username', 'user__role').annotate(count=Count('id')).order_by('-count')
for uc in user_counts:
    print(f"{uc['user__username']:15} ({uc['user__role']:10}) - {uc['count']} notifications")

# Check unread notifications
print("\nUnread Notifications:")
print("-" * 60)
unread = Notification.objects.filter(is_read=False)
print(f"Total unread: {unread.count()}")
for n in unread[:5]:
    print(f"  • {n.user.username}: {n.title}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\nTo see notifications in the app:")
print("1. Restart the backend server: python manage.py runserver")
print("2. Log out and log back in to the frontend")
print("3. Click the notification bell icon in the top right")
print("=" * 60)
