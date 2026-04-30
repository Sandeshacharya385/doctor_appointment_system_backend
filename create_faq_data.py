import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_appointment.settings')
django.setup()

from faqs.models import FAQ

# Clear existing FAQs
FAQ.objects.all().delete()

# Create sample FAQs
faqs_data = [
    {
        'question': 'How do I book an appointment?',
        'answer': 'To book an appointment, navigate to the "Find Doctors" page, select your preferred doctor, and click "Book Appointment". Choose your preferred date and time, provide the reason for visit, and submit the form.',
        'category': 'Appointments',
        'order': 1
    },
    {
        'question': 'Can I cancel or reschedule my appointment?',
        'answer': 'Yes, you can cancel your appointment from the "My Appointments" page. Click on the appointment you wish to cancel and select "Cancel". For rescheduling, please cancel the existing appointment and book a new one.',
        'category': 'Appointments',
        'order': 2
    },
    {
        'question': 'How do I view my prescriptions?',
        'answer': 'After your appointment is completed and the doctor has issued a prescription, you can view it in the "Prescriptions" section. All your past prescriptions are stored there for your reference.',
        'category': 'Prescriptions',
        'order': 3
    },
    {
        'question': 'What payment methods are accepted?',
        'answer': 'We accept various payment methods including credit/debit cards, digital wallets, and online banking. Payment is required at the time of booking to confirm your appointment.',
        'category': 'Payments',
        'order': 4
    },
    {
        'question': 'How do I update my profile information?',
        'answer': 'Go to "Profile Settings" from the sidebar menu. You can update your personal information, contact details, and profile picture. Don\'t forget to click "Save Changes" after making updates.',
        'category': 'Account',
        'order': 5
    },
    {
        'question': 'Is my medical information secure?',
        'answer': 'Yes, we take data security very seriously. All your medical information is encrypted and stored securely. We comply with healthcare data protection regulations and never share your information without your consent.',
        'category': 'Privacy',
        'order': 6
    },
    {
        'question': 'How do I enable dark mode?',
        'answer': 'You can enable dark mode by clicking the sun/moon icon in the top right corner, or by going to Preferences > Appearance and selecting "Dark" theme. You can also set it to follow your system preference.',
        'category': 'Settings',
        'order': 7
    },
    {
        'question': 'What should I do if I forget my password?',
        'answer': 'On the login page, click "Forgot Password" and enter your registered email address. You will receive instructions to reset your password. If you don\'t receive the email, please contact support.',
        'category': 'Account',
        'order': 8
    },
]

for faq_data in faqs_data:
    FAQ.objects.create(**faq_data)

print(f"Successfully created {len(faqs_data)} FAQs!")
