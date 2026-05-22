from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import MatchResult


@login_required
def match_detail(request, pk): # View details of a specific match result for involved users
    """
    View details of a specific match result.
    RBAC enforced: only the involved family or hospital user can view.
    Police can view any regional match via their own views , meaning they can access matches even if not directly involved.
    """
    match = get_object_or_404(MatchResult, pk=pk) # Get the match result i.e. the specific MatchResult instance which is being viewed: For displaying match details
    user = request.user # Get the current user

    # Family can only see their own report's matches
    if user.role == 'FAMILY' and match.missing_person.linked_family_user != user: # Check if the user is linked to the missing person
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    # Hospital can only see their own patient's matches
    if user.role == 'HOSPITAL' and match.unidentified_patient.linked_hospital != user: # Check if the user is linked to the unidentified patient
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    return render(request, 'matching/match_detail.html', {'match': match})

# This view is responsible for displaying the details of a specific match result for all involved users.
# For Police users, they can view any regional match via their own views.