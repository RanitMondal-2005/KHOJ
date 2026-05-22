from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin): # Admin interface for managing notifications
    list_display = ['user', 'notif_type', 'is_read', 'created_at']
    list_filter = ['notif_type', 'is_read']
    search_fields = ['user__email', 'message']
    readonly_fields = ['created_at']
