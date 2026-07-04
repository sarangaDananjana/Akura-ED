from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser with all custom fields visible."""

    list_display = ('username', 'email', 'role', 'is_premium', 'daily_flashcard_limit', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('role', 'is_premium', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')

    # Add custom fields to the existing UserAdmin fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('Akura Profile', {
            'fields': ('role', 'is_premium', 'daily_flashcard_limit', 'phone_number', 'profile_photo', 'auth_version'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Akura Profile', {
            'fields': ('role', 'is_premium', 'daily_flashcard_limit', 'phone_number', 'profile_photo'),
        }),
    )

    readonly_fields = ('auth_version',)
