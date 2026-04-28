from rest_framework import serializers
from .models import Appointment, Prescription, Medicine
from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from users.serializers import UserSerializer


class MedicineSerializer(serializers.ModelSerializer):
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    name = serializers.CharField(
        max_length=200,
        help_text='Name of the medicine or drug'
    )
    dosage = serializers.CharField(
        max_length=100,
        help_text='Dosage amount and unit (e.g., 500mg, 10ml)'
    )
    frequency = serializers.ChoiceField(
        choices=[
            ('once_daily', 'Once Daily'),
            ('twice_daily', 'Twice Daily'),
            ('three_times_daily', 'Three Times Daily'),
            ('four_times_daily', 'Four Times Daily'),
            ('every_morning', 'Every Morning'),
            ('every_night', 'Every Night'),
            ('before_meal', 'Before Meal'),
            ('after_meal', 'After Meal'),
            ('as_needed', 'As Needed'),
        ],
        help_text='Frequency of medication intake'
    )
    duration_days = serializers.IntegerField(
        help_text='Duration of medication in days'
    )
    timing_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Additional timing instructions (e.g., after meals, before bed)'
    )

    class Meta:
        model = Medicine
        fields = ['id', 'name', 'dosage', 'frequency', 'frequency_display', 'duration_days', 'timing_notes']


class PrescriptionSerializer(serializers.ModelSerializer):
    medicines = MedicineSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = ['id', 'appointment', 'diagnosis', 'instructions', 'medicines', 'created_at']
        read_only_fields = ['appointment', 'created_at']


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    medicines = MedicineSerializer(many=True)
    diagnosis = serializers.CharField(
        max_length=500,
        help_text='Medical diagnosis or condition identified by the doctor'
    )
    instructions = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Additional instructions for the patient (e.g., dietary advice, precautions)'
    )

    class Meta:
        model = Prescription
        fields = ['diagnosis', 'instructions', 'medicines']

    def create(self, validated_data):
        medicines_data = validated_data.pop('medicines')
        prescription = Prescription.objects.create(**validated_data)
        for med in medicines_data:
            Medicine.objects.create(prescription=prescription, **med)
        return prescription

    def update(self, instance, validated_data):
        medicines_data = validated_data.pop('medicines', [])
        instance.diagnosis = validated_data.get('diagnosis', instance.diagnosis)
        instance.instructions = validated_data.get('instructions', instance.instructions)
        instance.save()
        if medicines_data:
            instance.medicines.all().delete()
            for med in medicines_data:
                Medicine.objects.create(prescription=instance, **med)
        return instance


class AppointmentSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    prescription = PrescriptionSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'doctor_details', 'appointment_date',
                  'appointment_time', 'status', 'reason', 'notes', 'prescription', 'created_at']
        read_only_fields = ['patient', 'created_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.filter(is_available=True),
        help_text='ID of the doctor to book appointment with (must be available)'
    )
    appointment_date = serializers.DateField(
        help_text='Appointment date in YYYY-MM-DD format'
    )
    appointment_time = serializers.TimeField(
        help_text='Appointment time in HH:MM format (30-minute slots, e.g., 09:00, 09:30)'
    )
    reason = serializers.CharField(
        max_length=500,
        help_text='Reason for appointment or symptoms description'
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']

    def validate(self, attrs):
        from doctors.models import DoctorAvailability
        import datetime

        doctor = attrs['doctor']
        date = attrs['appointment_date']
        time = attrs['appointment_time']

        # Check slot not already booked
        if Appointment.objects.filter(
            doctor=doctor,
            appointment_date=date,
            appointment_time=time,
            status__in=['pending', 'confirmed']
        ).exists():
            raise serializers.ValidationError("This time slot is already booked.")

        # Check doctor availability for that day
        day_of_week = date.weekday()  # 0=Monday
        availability = DoctorAvailability.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_active=True
        )
        if not availability.exists():
            raise serializers.ValidationError("Doctor is not available on this day.")

        # Check time is within any available slot
        in_slot = any(a.start_time <= time <= a.end_time for a in availability)
        if not in_slot:
            raise serializers.ValidationError("Selected time is outside doctor's available hours.")

        return attrs


class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status', 'notes']
