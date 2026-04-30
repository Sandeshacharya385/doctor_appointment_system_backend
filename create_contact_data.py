import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_appointment.settings')
django.setup()

from settings_app.models import ContactInformation

# Create or update contact information
contact, created = ContactInformation.objects.get_or_create(
    id=1,
    defaults={
        'email': 'support@medibook.com',
        'phone': '+1 (234) 567-890',
        'address': '123 Healthcare Ave, Medical District, City, State 12345',
        'working_hours': 'Mon-Fri, 9AM-6PM',
        'emergency_contact': '+1 (234) 567-999'
    }
)

if created:
    print("Contact information created successfully!")
else:
    print("Contact information already exists!")
