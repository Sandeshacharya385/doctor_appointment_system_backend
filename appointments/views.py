from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Appointment, Prescription
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer,
    AppointmentStatusSerializer, PrescriptionCreateSerializer, PrescriptionSerializer
)


class AppointmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'doctor':
            return Appointment.objects.filter(doctor__user=user).select_related(
                'patient', 'doctor__user'
            ).prefetch_related('prescription__medicines')
        if user.role == 'admin':
            return Appointment.objects.all().select_related(
                'patient', 'doctor__user'
            ).prefetch_related('prescription__medicines')
        return Appointment.objects.filter(patient=user).select_related(
            'patient', 'doctor__user'
        ).prefetch_related('prescription__medicines')

    def perform_create(self, serializer):
        if self.request.user.role != 'patient':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only patients can book appointments.")
        serializer.save(patient=self.request.user)


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AppointmentStatusSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'doctor':
            return Appointment.objects.filter(doctor__user=user)
        if user.role == 'admin':
            return Appointment.objects.all()
        return Appointment.objects.filter(patient=user)


class PrescriptionCreateUpdateView(APIView):
    """Doctor writes/updates prescription for their appointment."""
    permission_classes = [IsAuthenticated]

    def get_appointment(self, appointment_id, user):
        try:
            return Appointment.objects.get(id=appointment_id, doctor__user=user)
        except Appointment.DoesNotExist:
            return None

    def post(self, request, appointment_id):
        if request.user.role != 'doctor':
            return Response({'error': 'Only doctors can prescribe.'}, status=status.HTTP_403_FORBIDDEN)
        appt = self.get_appointment(appointment_id, request.user)
        if not appt:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
        if hasattr(appt, 'prescription'):
            serializer = PrescriptionCreateSerializer(appt.prescription, data=request.data)
        else:
            serializer = PrescriptionCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(appointment=appt)
            appt.status = 'completed'
            appt.save()
            return Response(PrescriptionSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, appointment_id):
        """Both doctor and patient can view the prescription."""
        user = request.user
        try:
            if user.role == 'doctor':
                appt = Appointment.objects.get(id=appointment_id, doctor__user=user)
            elif user.role == 'patient':
                appt = Appointment.objects.get(id=appointment_id, patient=user)
            else:
                appt = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not hasattr(appt, 'prescription'):
            return Response({'error': 'No prescription yet.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PrescriptionSerializer(appt.prescription).data)


class PatientPrescriptionsView(APIView):
    """Patient views all their prescriptions across appointments."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'patient':
            return Response({'error': 'Patients only.'}, status=status.HTTP_403_FORBIDDEN)
        appointments = Appointment.objects.filter(
            patient=request.user, status='completed'
        ).prefetch_related('prescription__medicines').select_related('doctor__user')
        result = []
        for appt in appointments:
            if hasattr(appt, 'prescription'):
                data = PrescriptionSerializer(appt.prescription).data
                data['appointment_date'] = str(appt.appointment_date)
                data['doctor_name'] = f"Dr. {appt.doctor.user.get_full_name()}"
                data['specialization'] = appt.doctor.specialization
                result.append(data)
        return Response(result)


class PatientHistoryView(APIView):
    """Doctor views full history of a specific patient — all appointments + prescriptions."""
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        if request.user.role not in ('doctor', 'admin'):
            return Response({'error': 'Doctors and admins only.'}, status=status.HTTP_403_FORBIDDEN)

        from users.models import User
        try:
            patient = User.objects.get(id=patient_id, role='patient')
        except User.DoesNotExist:
            return Response({'error': 'Patient not found.'}, status=status.HTTP_404_NOT_FOUND)

        # All appointments for this patient (across all doctors)
        appointments = Appointment.objects.filter(
            patient=patient
        ).select_related('doctor__user').prefetch_related(
            'prescription__medicines'
        ).order_by('-appointment_date', '-appointment_time')

        history = []
        for appt in appointments:
            entry = {
                'id': appt.id,
                'appointment_date': str(appt.appointment_date),
                'appointment_time': str(appt.appointment_time),
                'status': appt.status,
                'reason': appt.reason,
                'notes': appt.notes,
                'doctor_name': f"Dr. {appt.doctor.user.get_full_name()}",
                'specialization': appt.doctor.specialization,
                'is_followup': False,
                'prescription': None,
            }
            if hasattr(appt, 'prescription'):
                entry['prescription'] = PrescriptionSerializer(appt.prescription).data
            history.append(entry)

        # Mark follow-ups: appointments after the first one with the same doctor
        seen_doctors: dict = {}
        for entry in reversed(history):  # oldest first
            doc = entry['doctor_name']
            if doc in seen_doctors:
                entry['is_followup'] = True
            else:
                seen_doctors[doc] = True

        return Response({
            'patient': {
                'id': patient.id,
                'name': patient.get_full_name() or patient.username,
                'email': patient.email,
                'phone': getattr(patient, 'phone', ''),
            },
            'total_visits': len(history),
            'history': history,
        })
