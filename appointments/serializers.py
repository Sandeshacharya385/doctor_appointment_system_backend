from rest_framework import serializers
from .models import Appointment
from doctors.serializers import DoctorSerializer
from users.serializers import UserSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'doctor_details', 'appointment_date',
                  'appointment_time', 'status', 'reason', 'notes', 'created_at']
        read_only_fields = ['patient', 'created_at']

class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']
    
    def validate(self, attrs):
        if Appointment.objects.filter(
            doctor=attrs['doctor'],
            appointment_date=attrs['appointment_date'],
            appointment_time=attrs['appointment_time'],
            status__in=['pending', 'confirmed']
        ).exists():
            raise serializers.ValidationError("This time slot is already booked")
        return attrs
