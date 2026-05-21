from django.contrib import admin
from .models import UnidentifiedPatient


@admin.register(UnidentifiedPatient)
class UnidentifiedPatientAdmin(admin.ModelAdmin):
    list_display = ['estimated_name', 'linked_hospital', 'district', 'status', 'admission_date']
    list_filter = ['status', 'gender', 'district']
    search_fields = ['estimated_name', 'district', 'found_location']
    readonly_fields = ['created_at', 'updated_at']
