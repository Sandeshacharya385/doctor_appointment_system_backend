from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    appointment = serializers.PrimaryKeyRelatedField(
        read_only=True,
        help_text='ID of the associated appointment'
    )
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Payment amount in local currency'
    )
    status = serializers.ChoiceField(
        choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')],
        help_text='Payment status: pending, completed, failed, or refunded'
    )
    payment_method = serializers.CharField(
        max_length=50,
        help_text='Payment method used (e.g., credit_card, debit_card, cash, insurance)'
    )
    transaction_id = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text='Unique transaction identifier from payment gateway'
    )
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
