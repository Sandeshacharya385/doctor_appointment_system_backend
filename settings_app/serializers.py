from rest_framework import serializers
from .models import ContactInformation

class ContactInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInformation
        fields = ['id', 'email', 'phone', 'address', 'working_hours', 'emergency_contact', 'updated_at']
        read_only_fields = ['updated_at']
