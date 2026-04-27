from rest_framework import serializers
from .models import Review
from users.serializers import UserSerializer
from doctors.models import Doctor

class ReviewSerializer(serializers.ModelSerializer):
    patient = UserSerializer(
        read_only=True,
        help_text='Patient who wrote the review'
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        help_text='ID of the doctor being reviewed'
    )
    rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
        help_text='Rating from 1 to 5 stars (1=poor, 5=excellent)'
    )
    comment = serializers.CharField(
        help_text='Review comment describing the experience with the doctor'
    )
    
    class Meta:
        model = Review
        fields = ['id', 'patient', 'doctor', 'rating', 'comment', 'created_at']
        read_only_fields = ['patient', 'created_at']
