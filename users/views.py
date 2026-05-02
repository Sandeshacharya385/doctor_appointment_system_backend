from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import User
from .serializers import RegisterSerializer, UserSerializer


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='Register new user',
        description='Create a new user account with role (patient, doctor, or admin). Doctors should be created via admin endpoint.',
        request=RegisterSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Patient Registration',
                value={
                    'username': 'john_doe',
                    'email': 'john@example.com',
                    'password': 'SecurePass123!',
                    'password2': 'SecurePass123!',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'role': 'patient',
                    'phone': '+1234567890'
                },
                request_only=True,
            ),
        ],
    )
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        # Check if username already exists
        username = request.data.get('username')
        if username and User.objects.filter(username=username).exists():
            return Response(
                {'detail': 'A user with this username already exists. Please choose a different username.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if email already exists
        email = request.data.get('email')
        if email and User.objects.filter(email=email).exists():
            return Response(
                {'detail': 'A user with this email already exists. Please use a different email address.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Proceed with normal registration
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema_view(
    get=extend_schema(
        tags=['Authentication'],
        summary='Get current user profile',
        description='Retrieve authenticated user profile information including personal details, role, and contact information.',
        responses={
            200: UserSerializer,
            401: OpenApiTypes.OBJECT,
        },
    ),
    put=extend_schema(
        tags=['Authentication'],
        summary='Update user profile',
        description='Update authenticated user profile information. All fields must be provided.',
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
    ),
    patch=extend_schema(
        tags=['Authentication'],
        summary='Partially update user profile',
        description='Partially update authenticated user profile information. Only provided fields will be updated.',
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
    ),
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ── Admin-only views ──

class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'


@extend_schema(
    tags=['Admin'],
    summary='List all users',
    description='Admin-only endpoint to retrieve a list of all users in the system. Supports optional filtering by user role (patient, doctor, admin). Results are ordered by date joined (newest first).',
    parameters=[
        OpenApiParameter(
            name='role',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter users by role: patient, doctor, or admin',
            required=False,
            enum=['patient', 'doctor', 'admin'],
        ),
    ],
    responses={
        200: UserSerializer(many=True),
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
    },
)
class AdminUserListView(generics.ListAPIView):
    """Admin: list all users, optionally filter by role."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'admin':
            return User.objects.none()
        role = self.request.query_params.get('role')
        qs = User.objects.all().order_by('-date_joined')
        if role:
            qs = qs.filter(role=role)
        return qs


@extend_schema_view(
    get=extend_schema(
        tags=['Admin'],
        summary='Get user details',
        description='Admin-only endpoint to retrieve detailed information about a specific user by ID.',
        responses={
            200: UserSerializer,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
    put=extend_schema(
        tags=['Admin'],
        summary='Update user',
        description='Admin-only endpoint to update all fields of a specific user. All fields must be provided.',
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
    patch=extend_schema(
        tags=['Admin'],
        summary='Partially update user',
        description='Admin-only endpoint to partially update a specific user. Only provided fields will be updated.',
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
    delete=extend_schema(
        tags=['Admin'],
        summary='Delete user',
        description='Admin-only endpoint to delete a specific user. Admins cannot delete themselves.',
        responses={
            204: None,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
)
class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: get, update or delete any user."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'admin':
            return User.objects.none()
        return User.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == request.user:
            return Response({'error': 'Cannot delete yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Admin'],
    summary='Create doctor account',
    description='Admin-only endpoint to create a new user with doctor role and associated doctor profile. Creates both the user account and doctor profile in a single operation.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Unique username for the doctor'},
                'email': {'type': 'string', 'format': 'email', 'description': 'Doctor email address'},
                'password': {'type': 'string', 'description': 'Password for the account'},
                'first_name': {'type': 'string', 'description': 'Doctor first name'},
                'last_name': {'type': 'string', 'description': 'Doctor last name'},
                'phone': {'type': 'string', 'description': 'Contact phone number'},
                'specialization': {'type': 'string', 'description': 'Medical specialization (e.g., Cardiology, Dermatology)'},
                'qualification': {'type': 'string', 'description': 'Medical qualifications and degrees'},
                'experience_years': {'type': 'integer', 'description': 'Years of medical experience'},
                'consultation_fee': {'type': 'number', 'format': 'decimal', 'description': 'Consultation fee amount'},
                'bio': {'type': 'string', 'description': 'Doctor biography and additional information'},
            },
            'required': ['username', 'email', 'password'],
        }
    },
    responses={
        201: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'example': 'Doctor created successfully.'}
            }
        },
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Create Doctor',
            value={
                'username': 'dr_smith',
                'email': 'dr.smith@hospital.com',
                'password': 'SecurePass123!',
                'first_name': 'John',
                'last_name': 'Smith',
                'phone': '+1234567890',
                'specialization': 'Cardiology',
                'qualification': 'MBBS, MD Cardiology',
                'experience_years': 10,
                'consultation_fee': 150.00,
                'bio': 'Experienced cardiologist specializing in heart disease prevention and treatment.'
            },
            request_only=True,
        ),
    ],
)
class AdminCreateDoctorView(APIView):
    """Admin: create a user with role=doctor and their doctor profile."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Admin only.'}, status=status.HTTP_403_FORBIDDEN)

        from doctors.models import Doctor
        from doctors.serializers import DoctorProfileUpdateSerializer

        data = request.data
        # Create user
        user_data = {
            'username': data.get('username'),
            'email': data.get('email'),
            'password': data.get('password'),
            'password2': data.get('password'),
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'role': 'doctor',
            'phone': data.get('phone', ''),
        }
        user_ser = RegisterSerializer(data=user_data)
        if not user_ser.is_valid():
            return Response(user_ser.errors, status=status.HTTP_400_BAD_REQUEST)
        user = user_ser.save()

        # Create doctor profile
        Doctor.objects.create(
            user=user,
            specialization=data.get('specialization', ''),
            qualification=data.get('qualification', ''),
            experience_years=data.get('experience_years', 0),
            consultation_fee=data.get('consultation_fee', 0),
            bio=data.get('bio', ''),
        )
        return Response({'message': 'Doctor created successfully.'}, status=status.HTTP_201_CREATED)
