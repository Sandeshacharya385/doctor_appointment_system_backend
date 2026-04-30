from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ContactInformation
from .serializers import ContactInformationSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        summary="Get contact information",
        description="Get the system contact information",
        tags=['Settings']
    ),
    retrieve=extend_schema(
        summary="Get contact information details",
        description="Get detailed contact information",
        tags=['Settings']
    ),
    update=extend_schema(
        summary="Update contact information",
        description="Update contact information (Admin only)",
        tags=['Settings']
    ),
    partial_update=extend_schema(
        summary="Partially update contact information",
        description="Partially update contact information (Admin only)",
        tags=['Settings']
    ),
)
class ContactInformationViewSet(viewsets.ModelViewSet):
    serializer_class = ContactInformationSerializer
    queryset = ContactInformation.objects.all()
    http_method_names = ['get', 'put', 'patch']  # No POST or DELETE
    
    def get_permissions(self):
        # Only admin can update
        if self.action in ['update', 'partial_update']:
            return [permissions.IsAdminUser()]
        # Anyone can view
        return [permissions.AllowAny()]
    
    @extend_schema(
        summary="Get current contact information",
        description="Get the current system contact information",
        tags=['Settings']
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current contact information"""
        contact_info = ContactInformation.objects.first()
        if contact_info:
            serializer = self.get_serializer(contact_info)
            return Response(serializer.data)
        return Response({
            'email': 'support@medibook.com',
            'phone': '+1 (234) 567-890',
            'address': '123 Healthcare Ave, Medical District, City, State 12345',
            'working_hours': 'Mon-Fri, 9AM-6PM',
            'emergency_contact': '+1 (234) 567-999'
        })
