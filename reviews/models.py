from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from doctors.models import Doctor

class Review(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['patient', 'doctor']
    
    def __str__(self):
        return f"{self.patient.username} - Dr. {self.doctor.user.username} ({self.rating}★)"
