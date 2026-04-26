from rest_framework import serializers
from .models import Doctor, DoctorAvailability
from users.serializers import UserSerializer


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = DoctorAvailability
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_active']


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    availability = DoctorAvailabilitySerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialization', 'qualification', 'experience_years',
                  'consultation_fee', 'bio', 'is_available', 'availability', 'created_at']


class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    """Allows doctor to update their own profile fields."""
    class Meta:
        model = Doctor
        fields = ['consultation_fee', 'bio', 'is_available', 'specialization', 'qualification', 'experience_years']
