from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Doctor, DoctorAvailability
from .serializers import DoctorSerializer, DoctorAvailabilitySerializer, DoctorProfileUpdateSerializer


class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.filter(is_available=True)
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'specialization']
    ordering_fields = ['consultation_fee', 'experience_years']


class DoctorDetailView(generics.RetrieveAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]


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
