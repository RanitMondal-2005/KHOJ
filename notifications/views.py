"""notifications/views.py"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notification_list(request): # View for listing notifications
    """Show all notifications for the current user."""
    notifications = Notification.objects.filter(user=request.user) # Get all notifications for the user
    notifications.filter(is_read=False).update(is_read=True) # Mark notifications as read
    return render(request, 'notifications/list.html', {'notifications': notifications}) # Render the notification list template
