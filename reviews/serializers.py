from rest_framework import serializers
from .models import Review
from users.serializers import UserSerializer

class ReviewSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'patient', 'doctor', 'rating', 'comment', 'created_at']
        read_only_fields = ['patient', 'created_at']
