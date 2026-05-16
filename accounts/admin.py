"""
accounts/admin.py

Django admin registrations for developer use only.
Not part of the platform's core RBAC — only for DB inspection.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import KhojUser, HospitalProfile, PoliceProfile

# Customize admin site branding
admin.site.site_header = "Khoj Developer Admin"
admin.site.site_title = "Khoj Admin"
admin.site.index_title = "Database Inspection Panel"


@admin.register(KhojUser)
class KhojUserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'full_name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('full_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['date_joined', 'last_login']


@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display = ['hospital_name', 'staff_id', 'district', 'emergency_contact']
    search_fields = ['hospital_name', 'staff_id', 'district']
    list_filter = ['district']


@admin.register(PoliceProfile)
class PoliceProfileAdmin(admin.ModelAdmin):
    list_display = ['police_station_name', 'police_id', 'district']
    search_fields = ['police_station_name', 'police_id', 'district']
    list_filter = ['district']
