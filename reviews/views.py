from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Review
from .serializers import ReviewSerializer

@extend_schema_view(
    get=extend_schema(
        tags=['Reviews'],
        summary='List doctor reviews',
        description='Retrieve list of reviews. Optionally filter by doctor ID using the doctor query parameter.',
        parameters=[
            OpenApiParameter(
                name='doctor',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter reviews by doctor ID',
                required=False,
            ),
        ],
        responses={
            200: ReviewSerializer(many=True),
            401: OpenApiTypes.OBJECT,
        },
    ),
    post=extend_schema(
        tags=['Reviews'],
        summary='Create doctor review',
        description='Create a new review for a doctor. Patients can only review doctors they have had appointments with. One review per doctor per patient.',
        request=ReviewSerializer,
        responses={
            201: ReviewSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
    ),
)
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
