import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_appointment.settings')
django.setup()

from users.models import User
from doctors.models import Doctor, DoctorAvailability

# Create test doctors
doctors_data = [
    {
        'username': 'drsmith',
        'email': 'drsmith@hospital.com',
        'password': 'doctor123',
        'first_name': 'John',
        'last_name': 'Smith',
        'specialization': 'Cardiologist',
        'qualification': 'MBBS, MD (Cardiology)',
        'experience_years': 15,
        'consultation_fee': 150.00,
        'bio': 'Experienced cardiologist specializing in heart disease prevention and treatment.'
    },
    {
        'username': 'drjohnson',
        'email': 'drjohnson@hospital.com',
        'password': 'doctor123',
        'first_name': 'Sarah',
        'last_name': 'Johnson',
        'specialization': 'Pediatrician',
        'qualification': 'MBBS, MD (Pediatrics)',
        'experience_years': 10,
        'consultation_fee': 120.00,
        'bio': 'Dedicated pediatrician with expertise in child healthcare and development.'
    },
    {
        'username': 'drwilliams',
        'email': 'drwilliams@hospital.com',
        'password': 'doctor123',
        'first_name': 'Michael',
        'last_name': 'Williams',
        'specialization': 'Orthopedic Surgeon',
        'qualification': 'MBBS, MS (Orthopedics)',
        'experience_years': 12,
        'consultation_fee': 180.00,
        'bio': 'Skilled orthopedic surgeon specializing in joint replacement and sports injuries.'
    }
]

print('Creating test doctors...\n')

for doctor_data in doctors_data:
    # Check if user already exists
    if User.objects.filter(username=doctor_data['username']).exists():
        print(f"⚠️  Doctor {doctor_data['username']} already exists, skipping...")
        continue
    
    # Create doctor user
    user = User.objects.create_user(
        username=doctor_data['username'],
        email=doctor_data['email'],
        password=doctor_data['password'],
        first_name=doctor_data['first_name'],
        last_name=doctor_data['last_name'],
        role='doctor'
    )
    
    # Create doctor profile
    doctor = Doctor.objects.create(
        user=user,
        specialization=doctor_data['specialization'],
        qualification=doctor_data['qualification'],
        experience_years=doctor_data['experience_years'],
        consultation_fee=doctor_data['consultation_fee'],
        bio=doctor_data['bio']
    )
    
    # Add availability (Monday to Friday, 9 AM to 5 PM)
    for day in range(5):
        DoctorAvailability.objects.create(
            doctor=doctor,
            day_of_week=day,
            start_time='09:00',
            end_time='17:00'
        )
    
    print(f"✅ Created Dr. {doctor_data['first_name']} {doctor_data['last_name']} - {doctor_data['specialization']}")

print('\n✨ Test data created successfully!')
print('\nTest Doctor Credentials:')
print('Username: drsmith | Password: doctor123')
print('Username: drjohnson | Password: doctor123')
print('Username: drwilliams | Password: doctor123')
