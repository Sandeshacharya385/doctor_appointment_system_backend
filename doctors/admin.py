from django.contrib import admin
from .models import Doctor, DoctorAvailability

class DoctorAvailabilityInline(admin.TabularInline):
    model = DoctorAvailability
    extra = 1

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'experience_years', 'consultation_fee', 'is_available']
    list_filter = ['specialization', 'is_available']
    search_fields = ['user__username', 'user__email', 'specialization']
    inlines = [DoctorAvailabilityInline]
