import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_appointment.settings')
django.setup()

from notifications.services import NotificationService
from users.models import User
from appointments.models import Appointment

# Test notification creation
print("Testing notification system...")

# Get a test user
try:
    test_user = User.objects.filter(role='patient').first()
    if test_user:
        print(f"Found test user: {test_user.username}")
        
        # Create a test notification
        notification = NotificationService.create_notification(
            user=test_user,
            title="Test Notification",
            message="This is a test notification to verify the system is working."
        )
        print(f"✓ Notification created successfully: ID {notification.id}")
        
        # Test appointment booking notification
        appointment = Appointment.objects.filter(patient=test_user).first()
        if appointment:
            print(f"Found test appointment: ID {appointment.id}")
            try:
                NotificationService.notify_appointment_booked(appointment)
                print("✓ Appointment booking notification created successfully")
            except Exception as e:
                print(f"✗ Error creating appointment notification: {e}")
        else:
            print("No appointments found for testing")
    else:
        print("No test user found")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
