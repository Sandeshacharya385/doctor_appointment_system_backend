from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Doctor, DoctorAvailability
from .serializers import DoctorSerializer, DoctorAvailabilitySerializer, DoctorProfileUpdateSerializer


@extend_schema_view(
    get=extend_schema(
        tags=['Doctors'],
        summary='List all available doctors',
        description='Retrieve list of doctors with optional filtering by specialization and search by name. Results can be ordered by consultation fee or experience years.',
        parameters=[
            OpenApiParameter(
                name='specialization',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by doctor specialization (e.g., Cardiology, Dermatology, Pediatrics)',
                required=False,
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search by doctor first name, last name, or specialization',
                required=False,
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order by field: consultation_fee, -consultation_fee, experience_years, -experience_years (prefix with - for descending)',
                required=False,
            ),
        ],
        responses={
            200: DoctorSerializer(many=True),
        },
    )
)
class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.filter(is_available=True).select_related('user')  # Performance optimization
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'specialization']
    ordering_fields = ['consultation_fee', 'experience_years']


@extend_schema(
    tags=['Doctors'],
    summary='Get doctor details',
    description='Retrieve detailed information about a specific doctor including profile, specialization, availability schedule, and consultation fee.',
    responses={
        200: DoctorSerializer,
        404: OpenApiTypes.OBJECT,
    },
)
class DoctorDetailView(generics.RetrieveAPIView):
    queryset = Doctor.objects.all().select_related('user')  # Performance optimization
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    get=extend_schema(
        tags=['Doctors'],
        summary='Get doctor own profile',
        description='Doctor retrieves their own profile information including consultation fee, bio, availability status, and professional details. Requires doctor role authentication.',
        responses={
            200: DoctorSerializer,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
    patch=extend_schema(
        tags=['Doctors'],
        summary='Update doctor profile',
        description='Doctor updates their own profile fields including consultation fee, bio, availability status, specialization, qualification, and experience years. Requires doctor role authentication.',
        request=DoctorProfileUpdateSerializer,
        responses={
            200: DoctorSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
)
class DoctorProfileView(APIView):
    """Doctor manages their own profile — fee, bio, availability toggle."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'doctor':
            return Response({'error': 'Not a doctor.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            doctor = request.user.doctor_profile
        except Doctor.DoesNotExist:
            return Response({'error': 'Doctor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DoctorSerializer(doctor).data)

    def patch(self, request):
        if request.user.role != 'doctor':
            return Response({'error': 'Not a doctor.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            doctor = request.user.doctor_profile
        except Doctor.DoesNotExist:
            return Response({'error': 'Doctor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DoctorProfileUpdateSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(DoctorSerializer(doctor).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        tags=['Doctors'],
        summary='Get doctor availability slots',
        description='Doctor retrieves their own weekly availability schedule. Returns all availability slots with day, time range, and active status. Requires doctor role authentication.',
        responses={
            200: DoctorAvailabilitySerializer(many=True),
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
    ),
    post=extend_schema(
        tags=['Doctors'],
        summary='Create availability slot',
        description='Doctor creates a new availability slot for a specific day of the week with start and end times. Requires doctor role authentication.',
        request=DoctorAvailabilitySerializer,
        responses={
            201: DoctorAvailabilitySerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
    ),
)
class DoctorAvailabilityView(APIView):
    """Doctor manages their own availability slots."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'doctor':
            return Response({'error': 'Not a doctor.'}, status=status.HTTP_403_FORBIDDEN)
        doctor = request.user.doctor_profile
        slots = DoctorAvailability.objects.filter(doctor=doctor)
        return Response(DoctorAvailabilitySerializer(slots, many=True).data)

    def post(self, request):
        if request.user.role != 'doctor':
            return Response({'error': 'Not a doctor.'}, status=status.HTTP_403_FORBIDDEN)
        doctor = request.user.doctor_profile
        serializer = DoctorAvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=doctor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    patch=extend_schema(
        tags=['Doctors'],
        summary='Update availability slot',
        description='Doctor updates an existing availability slot. Can modify day, time range, or active status. Requires doctor role authentication.',
        request=DoctorAvailabilitySerializer,
        responses={
            200: DoctorAvailabilitySerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
    delete=extend_schema(
        tags=['Doctors'],
        summary='Delete availability slot',
        description='Doctor deletes an existing availability slot. Requires doctor role authentication.',
        responses={
            204: None,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
)
class DoctorAvailabilityDetailView(APIView):
    """Update or delete a single availability slot."""
    permission_classes = [IsAuthenticated]

    def get_slot(self, pk, user):
        try:
            return DoctorAvailability.objects.get(pk=pk, doctor__user=user)
        except DoctorAvailability.DoesNotExist:
            return None

    def patch(self, request, pk):
        slot = self.get_slot(pk, request.user)
        if not slot:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DoctorAvailabilitySerializer(slot, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        slot = self.get_slot(pk, request.user)
        if not slot:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        slot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Doctors'],
    summary='Get available time slots for doctor',
    description='Retrieve available 30-minute time slots for a specific doctor on a given date. Returns slots within doctor availability windows, marking which are already booked. Accessible to all users.',
    parameters=[
        OpenApiParameter(
            name='doctor_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Doctor ID',
            required=True,
        ),
        OpenApiParameter(
            name='date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Date in YYYY-MM-DD format to check availability',
            required=True,
        ),
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'slots': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'time': {'type': 'string', 'example': '09:00'},
                            'available': {'type': 'boolean', 'example': True},
                        }
                    }
                },
                'message': {'type': 'string', 'example': 'Doctor not available on this day.'}
            }
        },
        400: OpenApiTypes.OBJECT,
    },
)
class DoctorAvailableSlotsView(APIView):
    """Return available time slots for a doctor on a given date (for patients)."""
    permission_classes = [AllowAny]

    def get(self, request, doctor_id):
        from appointments.models import Appointment
        import datetime

        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'date param required (YYYY-MM-DD)'}, status=400)

        try:
            date = datetime.date.fromisoformat(date_str)
        except ValueError:
            return Response({'error': 'Invalid date format.'}, status=400)

        day_of_week = date.weekday()
        slots = DoctorAvailability.objects.filter(
            doctor_id=doctor_id, day_of_week=day_of_week, is_active=True
        )
        if not slots.exists():
            return Response({'slots': [], 'message': 'Doctor not available on this day.'})

        # Build 30-min time slots within availability windows
        booked_times = set(
            Appointment.objects.filter(
                doctor_id=doctor_id,
                appointment_date=date,
                status__in=['pending', 'confirmed']
            ).values_list('appointment_time', flat=True)
        )

        available = []
        for slot in slots:
            current = datetime.datetime.combine(date, slot.start_time)
            end = datetime.datetime.combine(date, slot.end_time)
            while current < end:
                t = current.time()
                available.append({
                    'time': t.strftime('%H:%M'),
                    'available': t not in booked_times
                })
                current += datetime.timedelta(minutes=30)

        return Response({'slots': available})
