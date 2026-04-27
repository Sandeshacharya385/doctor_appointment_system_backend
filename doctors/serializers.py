from rest_framework import serializers
from .models import Doctor, DoctorAvailability
from users.serializers import UserSerializer


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True,
        help_text='Human-readable day name (e.g., Monday, Tuesday)'
    )
    day_of_week = serializers.IntegerField(
        help_text='Day of week as integer (0=Monday, 1=Tuesday, ..., 6=Sunday)'
    )
    start_time = serializers.TimeField(
        help_text='Availability start time in HH:MM format (24-hour)'
    )
    end_time = serializers.TimeField(
        help_text='Availability end time in HH:MM format (24-hour)'
    )
    is_active = serializers.BooleanField(
        default=True,
        help_text='Whether this availability slot is currently active'
    )

    class Meta:
        model = DoctorAvailability
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_active']


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(
        read_only=True,
        help_text='User account information including name, email, and contact details'
    )
    availability = DoctorAvailabilitySerializer(
        many=True,
        read_only=True,
        help_text='Weekly availability schedule for the doctor'
    )
    specialization = serializers.CharField(
        help_text='Medical specialization (e.g., Cardiology, Dermatology, Pediatrics)'
    )
    qualification = serializers.CharField(
        help_text='Medical qualifications and degrees (e.g., MBBS, MD)'
    )
    experience_years = serializers.IntegerField(
        help_text='Years of medical practice experience'
    )
    consultation_fee = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Consultation fee amount in local currency'
    )
    bio = serializers.CharField(
        help_text='Doctor biography and additional professional information'
    )
    is_available = serializers.BooleanField(
        help_text='Whether the doctor is currently accepting appointments'
    )

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialization', 'qualification', 'experience_years',
                  'consultation_fee', 'bio', 'is_available', 'availability', 'created_at']


class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    """Allows doctor to update their own profile fields."""
    class Meta:
        model = Doctor
        fields = ['consultation_fee', 'bio', 'is_available', 'specialization', 'qualification', 'experience_years']
