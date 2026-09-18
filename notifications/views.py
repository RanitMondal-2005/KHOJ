"""notifications/views.py"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from matching.models import MatchResult
from .models import Notification


@login_required
def notification_list(request):
    """Show all notifications for the current user and detect active matches."""
    # 1. Base QuerySet
    user_notifs = Notification.objects.filter(user=request.user)

    # 2. Mark unread notifications as read in SQL BEFORE evaluating the queryset
    user_notifs.filter(is_read=False).update(is_read=True)

    # 3. Fetch all notifications fresh from DB
    notifications = list(user_notifs.order_by('-created_at'))

    # 4. Collect all related_match_ids from all fetched notifications which are NOT NONE
    match_ids = [n.related_match_id for n in notifications if n.related_match_id]

    # 5. Fetch only IDs that are still in 'PENDING' state
    active_match_ids = set(
        MatchResult.objects.filter(
            id__in=match_ids,
            status='PENDING'
        ).values_list('id', flat=True)
    )

    # 6. Render list
    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'active_match_ids': active_match_ids,
    })
