from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from .models import Payment
from .serializers import PaymentSerializer

@extend_schema_view(
    get=extend_schema(
        tags=['Payments'],
        summary='List user payments',
        description='Retrieve list of payments for the authenticated user. Patients see their own payments, doctors see payments for their appointments, admins see all payments.',
        responses={
            200: PaymentSerializer(many=True),
            401: OpenApiTypes.OBJECT,
        },
    )
)
class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(appointment__patient=self.request.user)
