"""
notifications/context_processors.py

PURPOSE:
- Injects `unread_notif_count` globally into every template context across the app.
- Powers the real-time red notification badge in the global navbar without requiring
  individual views to explicitly query or pass the count.

HOW IT WORKS:
1. Registered in `settings.TEMPLATES['OPTIONS']['context_processors']`.
2. This Context Processors are executed on every single page request that renders an HTML template using render().
3. Guards against unauthorized access:
   - Returns 0 for unauthenticated users.
4. Efficiently performs a direct SQL COUNT on unread notifications for the active user.
5. Injected value is accessible directly in HTML templates via: {{ unread_notif_count }}
"""


def unread_notifications(request):
    if not request.user.is_authenticated: # Check if User is Logged-in Or Not
        return {'unread_notif_count': 0}

    # Only family and hospital users receive notifications
    if request.user.role not in ('FAMILY', 'HOSPITAL'):
        return {'unread_notif_count': 0} # 'unread_notif_count' is the key for the unread notification count, which is made via the context processor, [ This is made by using the `unread_notifications` function ] and templates can access it via {{ unread_notif_count }}

    from .models import Notification
    count = Notification.objects.filter(user=request.user, is_read=False).count() # Count total no of unread notifications for the current user(filter by is_read=False flag to get only unread notifications)
    return {'unread_notif_count': count}
