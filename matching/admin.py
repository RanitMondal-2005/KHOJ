from django.contrib import admin
from .models import MatchResult


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ['missing_person', 'unidentified_patient', 'confidence_score', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['missing_person__person_name']
    readonly_fields = ['created_at', 'confidence_score']
    ordering = ['-confidence_score']
