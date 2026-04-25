from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Review
from .serializers import ReviewSerializer

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        doctor_id = self.request.query_params.get('doctor')
        if doctor_id:
            return Review.objects.filter(doctor_id=doctor_id)
        return Review.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)
