from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'created_at']
    list_filter = ['role', 'is_staff', 'is_active']
    
    # Make personal details read-only for admins
    readonly_fields = ['username', 'email', 'first_name', 'last_name', 'date_joined']
    
    fieldsets = (
        ('Personal Info (Read-Only)', {
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('Password', {
            'fields': ('password',),
            'description': 'Raw passwords are not stored, so there is no way to see this user\'s password, but you can change the password using <a href="../password/">this form</a>.'
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Additional Info', {
            'fields': ('role', 'phone', 'date_of_birth', 'address', 'profile_picture')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )
    
    # Prevent editing username and email in add form as well
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

