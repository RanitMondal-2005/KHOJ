# Context processor for notifications i.e. injecting unread notification count to every template context so that we can display it in the navbar
def unread_notifications(request):
    """
    Injects unread notification count into every template context.
    Used to display the notification badge in the navbar.
    Returns 0 for unauthenticated users and police (no notifications for police).
    """
    if not request.user.is_authenticated: # If user is not authenticated, meaning if user is not logged in, no notifications will be shown
        # user.is_authenticated means : the user is logged in and has a valid session, to check that is_authenticated is used
        return {'unread_notif_count': 0}

    # Only family and hospital users receive notifications
    if request.user.role not in ('FAMILY', 'HOSPITAL'): # If user is not family or hospital, no notifications will be shown,so return 0 to other users
        return {'unread_notif_count': 0} # 'unread_notif_count' is the key for the unread notification count, which is made via the context processor, [ This is made by using the `unread_notifications` function ] and templates can access it via {{ unread_notif_count }}

    from .models import Notification
    count = Notification.objects.filter(user=request.user, is_read=False).count() # Count unread notifications for the user, filtering by user and is_read=False to get only unread notifications, and then count() to get the total number of unread notifications
    return {'unread_notif_count': count}
