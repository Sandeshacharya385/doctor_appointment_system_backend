from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Appointment, Prescription
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer,
    AppointmentStatusSerializer, PrescriptionCreateSerializer, PrescriptionSerializer
)
from notifications.services import NotificationService


@extend_schema_view(
    get=extend_schema(
        tags=['Appointments'],
        summary='List appointments',
        description='List appointments filtered by user role: patients see their own appointments, doctors see appointments with them, admins see all appointments. Includes patient details, doctor details, and prescription information.',
        responses={
            200: AppointmentSerializer(many=True),
            401: OpenApiTypes.OBJECT,
        },
    ),
    post=extend_schema(
        tags=['Appointments'],
        summary='Book new appointment',
        description='Create a new appointment (patients only). Validates doctor availability for the selected date and time slot. Ensures the time slot is not already booked and falls within doctor availability hours.',
        request=AppointmentCreateSerializer,
        responses={
            201: AppointmentSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
    ),
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
        appointment = serializer.save(patient=self.request.user)
        
        # Send notification to doctor
        NotificationService.notify_appointment_booked(appointment)


@extend_schema_view(
    get=extend_schema(
        tags=['Appointments'],
        summary='Get appointment details',
        description='Retrieve detailed information about a specific appointment including patient, doctor, prescription, and status. Access filtered by user role.',
        responses={
            200: AppointmentSerializer,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
    put=extend_schema(
        tags=['Appointments'],
        summary='Update appointment status',
        description='Update appointment status and notes. Doctors can update status to confirmed or completed. Patients can cancel appointments.',
        request=AppointmentStatusSerializer,
        responses={
            200: AppointmentSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
    delete=extend_schema(
        tags=['Appointments'],
        summary='Cancel appointment',
        description='Cancel an appointment. Patients can cancel their own appointments. Doctors and admins can cancel any appointment.',
        responses={
            204: None,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
)
class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AppointmentStatusSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        # Optimize with select_related and prefetch_related to avoid N+1 queries
        base_queryset = Appointment.objects.select_related(
            'patient',
            'doctor',
            'doctor__user',
            'prescription'
        ).prefetch_related(
            'prescription__medicines'
        )
        
        if user.role == 'doctor':
            return base_queryset.filter(doctor__user=user)
        if user.role == 'admin':
            return base_queryset.all()
        return base_queryset.filter(patient=user)
    
    def perform_update(self, serializer):
        old_status = serializer.instance.status
        appointment = serializer.save()
        new_status = appointment.status
        
        # Send notifications based on status change
        if old_status != new_status:
            if new_status == 'confirmed':
                NotificationService.notify_appointment_confirmed(appointment)
            elif new_status == 'completed':
                NotificationService.notify_appointment_completed(appointment)
            elif new_status == 'cancelled':
                # Determine who cancelled
                cancelled_by = 'patient' if self.request.user.role == 'patient' else 'doctor'
                NotificationService.notify_appointment_cancelled(appointment, cancelled_by)
    
    def perform_destroy(self, instance):
        # Notify about cancellation before deleting
        cancelled_by = 'patient' if self.request.user.role == 'patient' else 'doctor'
        NotificationService.notify_appointment_cancelled(instance, cancelled_by)
        instance.status = 'cancelled'
        instance.save()


class PrescriptionCreateUpdateView(APIView):
    """Doctor writes/updates prescription for their appointment."""
    permission_classes = [IsAuthenticated]

    def get_appointment(self, appointment_id, user):
        try:
            # Optimize with select_related and prefetch_related
            return Appointment.objects.select_related(
                'doctor',
                'doctor__user',
                'prescription'
            ).prefetch_related(
                'prescription__medicines'
            ).get(id=appointment_id, doctor__user=user)
        except Appointment.DoesNotExist:
            return None

    @extend_schema(
        tags=['Appointments'],
        summary='Create or update prescription',
        description='Doctor creates or updates prescription for an appointment. Automatically marks appointment as completed. If prescription already exists, it will be updated with new data.',
        request=PrescriptionCreateSerializer,
        responses={
            201: PrescriptionSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request, appointment_id):
        if request.user.role != 'doctor':
            return Response({'error': 'Only doctors can prescribe.'}, status=status.HTTP_403_FORBIDDEN)
        appt = self.get_appointment(appointment_id, request.user)
        if not appt:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        is_new_prescription = not hasattr(appt, 'prescription')
        
        if hasattr(appt, 'prescription'):
            serializer = PrescriptionCreateSerializer(appt.prescription, data=request.data)
        else:
            serializer = PrescriptionCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(appointment=appt)
            appt.status = 'completed'
            appt.save()
            
            # Send notification to patient about new prescription
            if is_new_prescription:
                NotificationService.notify_prescription_issued(appt)
                NotificationService.notify_appointment_completed(appt)
            
            return Response(PrescriptionSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['Appointments'],
        summary='Get prescription',
        description='Retrieve prescription for an appointment. Accessible by the doctor who created it and the patient for whom it was prescribed. Returns prescription with diagnosis, instructions, and medicines.',
        responses={
            200: PrescriptionSerializer,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request, appointment_id):
        """Both doctor and patient can view the prescription."""
        user = request.user
        try:
            # Optimize with select_related and prefetch_related
            base_query = Appointment.objects.select_related(
                'doctor',
                'doctor__user',
                'prescription'
            ).prefetch_related(
                'prescription__medicines'
            )
            
            if user.role == 'doctor':
                appt = base_query.get(id=appointment_id, doctor__user=user)
            elif user.role == 'patient':
                appt = base_query.get(id=appointment_id, patient=user)
            else:
                appt = base_query.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not hasattr(appt, 'prescription'):
            return Response({'error': 'No prescription yet.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PrescriptionSerializer(appt.prescription).data)


@extend_schema(
    tags=['Appointments'],
    summary='Get patient prescriptions',
    description='Patient views all their prescriptions across completed appointments. Returns prescriptions with appointment date, doctor name, specialization, diagnosis, instructions, and medicines.',
    responses={
        200: {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'appointment': {'type': 'integer'},
                    'diagnosis': {'type': 'string'},
                    'instructions': {'type': 'string'},
                    'medicines': {'type': 'array'},
                    'appointment_date': {'type': 'string', 'format': 'date'},
                    'doctor_name': {'type': 'string'},
                    'specialization': {'type': 'string'},
                }
            }
        },
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
    },
)
class PatientPrescriptionsView(APIView):
    """Patient views all their prescriptions across appointments."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'patient':
            return Response({'error': 'Patients only.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Optimize with select_related and prefetch_related to avoid N+1 queries
        appointments = Appointment.objects.filter(
            patient=request.user, status='completed'
        ).select_related(
            'doctor',
            'doctor__user',
            'prescription'
        ).prefetch_related(
            'prescription__medicines'
        )
        
        result = []
        for appt in appointments:
            if hasattr(appt, 'prescription'):
                data = PrescriptionSerializer(appt.prescription).data
                data['appointment_date'] = str(appt.appointment_date)
                data['doctor_name'] = f"Dr. {appt.doctor.user.get_full_name()}"
                data['specialization'] = appt.doctor.specialization
                result.append(data)
        return Response(result)


@extend_schema(
    tags=['Appointments'],
    summary='Get patient history',
    description='Doctor or admin views full appointment history of a specific patient. Returns all appointments with prescriptions, ordered by date. Includes follow-up indicators and patient information.',
    parameters=[
        OpenApiParameter(
            name='patient_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Patient user ID',
            required=True,
        ),
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'patient': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'email': {'type': 'string'},
                        'phone': {'type': 'string'},
                    }
                },
                'total_visits': {'type': 'integer'},
                'history': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'appointment_date': {'type': 'string', 'format': 'date'},
                            'appointment_time': {'type': 'string', 'format': 'time'},
                            'status': {'type': 'string'},
                            'reason': {'type': 'string'},
                            'notes': {'type': 'string'},
                            'doctor_name': {'type': 'string'},
                            'specialization': {'type': 'string'},
                            'is_followup': {'type': 'boolean'},
                            'prescription': {'type': 'object', 'nullable': True},
                        }
                    }
                }
            }
        },
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)
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

        # Optimize with select_related and prefetch_related to avoid N+1 queries
        appointments = Appointment.objects.filter(
            patient=patient
        ).select_related(
            'doctor',
            'doctor__user',
            'prescription'
        ).prefetch_related(
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
