from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'role', 'phone', 'date_of_birth', 'address', 'profile_picture']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text='Password must be at least 8 characters with letters and numbers'
    )
    password2 = serializers.CharField(
        write_only=True,
        help_text='Confirm password (must match password field)'
    )
    first_name = serializers.CharField(
        required=True,
        help_text='User first name (required)'
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='User last name (optional)'
    )
    role = serializers.ChoiceField(
        choices=['patient', 'doctor', 'admin'],
        default='patient',
        help_text='User role: patient, doctor, or admin'
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Contact phone number with country code'
    )
    profile_picture = serializers.ImageField(
        required=False,
        allow_null=True,
        help_text='Optional profile picture (can be added later)'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 
                  'last_name', 'role', 'phone', 'profile_picture']
    
    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists. Please choose a different username.")
        return value
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists. Please use a different email address.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
