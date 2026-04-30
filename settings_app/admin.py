from django.contrib import admin
from .models import ContactInformation

@admin.register(ContactInformation)
class ContactInformationAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone', 'working_hours', 'updated_at']
    
    fieldsets = (
        ('Contact Details', {
            'fields': ('email', 'phone', 'emergency_contact')
        }),
        ('Location & Hours', {
            'fields': ('address', 'working_hours')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not ContactInformation.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
