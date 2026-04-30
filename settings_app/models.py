from django.db import models

class ContactInformation(models.Model):
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=50)
    address = models.TextField()
    working_hours = models.CharField(max_length=255, default='Mon-Fri, 9AM-6PM')
    emergency_contact = models.CharField(max_length=50, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Information'
        verbose_name_plural = 'Contact Information'

    def __str__(self):
        return f"Contact Info - {self.email}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and ContactInformation.objects.exists():
            # Update existing instance instead of creating new
            existing = ContactInformation.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
