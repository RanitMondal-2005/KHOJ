from django.contrib import admin
from .models import MissingPerson, CaseUpdate


@admin.register(MissingPerson)
class MissingPersonAdmin(admin.ModelAdmin):
    list_display = ['person_name', 'linked_family_user', 'district', 'status', 'last_seen_date', 'created_at']
    list_filter = ['status', 'gender', 'district']
    search_fields = ['person_name', 'district', 'last_seen_location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CaseUpdate)
class CaseUpdateAdmin(admin.ModelAdmin):
    list_display = ['linked_missing_person', 'created_at']
    readonly_fields = ['created_at']
