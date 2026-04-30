from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FAQ
from .serializers import FAQSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

@extend_schema_view(
    list=extend_schema(
        summary="List all FAQs",
        description="Get a list of all active FAQs ordered by display order",
        tags=['FAQs']
    ),
    retrieve=extend_schema(
        summary="Get FAQ details",
        description="Get detailed information about a specific FAQ",
        tags=['FAQs']
    ),
    create=extend_schema(
        summary="Create new FAQ",
        description="Create a new FAQ (Admin only)",
        tags=['FAQs']
    ),
    update=extend_schema(
        summary="Update FAQ",
        description="Update an existing FAQ (Admin only)",
        tags=['FAQs']
    ),
    partial_update=extend_schema(
        summary="Partially update FAQ",
        description="Partially update an existing FAQ (Admin only)",
        tags=['FAQs']
    ),
    destroy=extend_schema(
        summary="Delete FAQ",
        description="Delete an FAQ (Admin only)",
        tags=['FAQs']
    ),
)
class FAQViewSet(viewsets.ModelViewSet):
    serializer_class = FAQSerializer
    
    def get_queryset(self):
        # Admin can see all FAQs, others only see active ones
        if self.request.user.is_staff:
            return FAQ.objects.all()
        return FAQ.objects.filter(is_active=True)
    
    def get_permissions(self):
        # Only admin can create, update, or delete FAQs
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        # Anyone can view FAQs
        return [permissions.AllowAny()]
    
    @extend_schema(
        summary="Get FAQs by category",
        description="Get all active FAQs filtered by category",
        parameters=[
            OpenApiParameter(
                name='category',
                description='Category name to filter by',
                required=True,
                type=str
            )
        ],
        tags=['FAQs']
    )
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category = request.query_params.get('category', 'General')
        faqs = self.get_queryset().filter(category=category)
        serializer = self.get_serializer(faqs, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get all FAQ categories",
        description="Get a list of all unique FAQ categories",
        tags=['FAQs']
    )
    @action(detail=False, methods=['get'])
    def categories(self, request):
        categories = FAQ.objects.filter(is_active=True).values_list('category', flat=True).distinct()
        return Response(list(categories))
