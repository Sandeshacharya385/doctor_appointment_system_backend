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
    
    # Make user field read-only (cannot change which user is the doctor)
    readonly_fields = ['user', 'get_user_email', 'get_user_name']
    
    fieldsets = (
        ('Doctor User (Read-Only)', {
            'fields': ('user', 'get_user_name', 'get_user_email'),
            'description': 'User personal details can only be changed by the user themselves.'
        }),
        ('Professional Information', {
            'fields': ('specialization', 'qualification', 'experience_years', 'consultation_fee', 'bio', 'is_available')
        }),
    )
    
    def get_user_name(self, obj):
        """Display user's full name"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return "-"
    get_user_name.short_description = "User Name"
    
    def get_user_email(self, obj):
        """Display user's email"""
        return obj.user.email if obj.user else "-"
    get_user_email.short_description = "User Email"

