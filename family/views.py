from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from functools import wraps

from .models import MissingPerson, CaseUpdate
from .forms import MissingPersonForm, CaseUpdateForm
from matching.models import MatchResult
from notifications.models import Notification


def family_required(view_func):
    """Decorator to restrict view to family users only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'FAMILY':
            messages.error(request, "Access denied. This section is for family users only.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@family_required
def dashboard(request):
    """Family dashboard: overview of reports and matches."""
    user = request.user
    active_reports = MissingPerson.objects.filter(linked_family_user=user, status='ACTIVE')
    recent_matches = MatchResult.objects.filter(
        missing_person__linked_family_user=user
    ).exclude(
        status='REJECTED'
    ).order_by('-confidence_score')[:5]

    unread_count = Notification.objects.filter(user=user, is_read=False).count()

    context = {
        'active_reports': active_reports,
        'recent_matches': recent_matches,
        'active_count': active_reports.count(),
        'unread_count': unread_count,
    }
    return render(request, 'family/dashboard.html', context)


@family_required
def my_reports(request):
    """List all active missing person reports by this family user."""
    reports = MissingPerson.objects.filter(
        linked_family_user=request.user, status='ACTIVE'
    )
    return render(request, 'family/my_reports.html', {'reports': reports})


@family_required
def add_report(request):
    """Create a new missing person report (max 3 active cases)."""
    user = request.user
    active_count = MissingPerson.objects.filter(linked_family_user=user, status='ACTIVE').count()

    # Enforce the 3 active case limit
    if active_count >= 3:
        messages.warning(request, "You already have 3 active cases. Please close or resolve one before adding another.")
        return redirect('family:my_reports')

    if request.method == 'POST':
        form = MissingPersonForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.linked_family_user = user
            report.save()
            messages.success(request, f"Report for {report.person_name} has been filed. Matching will run automatically.")
            return redirect('family:my_reports')
    else:
        form = MissingPersonForm()

    return render(request, 'family/add_report.html', {
        'form': form,
        'active_count': active_count
    })


@family_required
def report_detail(request, pk):
    """View a single missing person report and its updates."""
    report = get_object_or_404(MissingPerson, pk=pk, linked_family_user=request.user)
    updates = report.case_updates.all()
    matches = MatchResult.objects.filter(missing_person=report).exclude(status='REJECTED').order_by('-confidence_score')

    context = {
        'report': report,
        'updates': updates,
        'matches': matches,
    }
    return render(request, 'family/report_detail.html', context)


@family_required
def add_case_update(request, pk):
    """Family user adds a clue/update to their case."""
    report = get_object_or_404(MissingPerson, pk=pk, linked_family_user=request.user)

    if report.status != 'ACTIVE':
        messages.warning(request, "Cannot add updates to a closed or resolved case.")
        return redirect('family:report_detail', pk=pk)

    if request.method == 'POST':
        form = CaseUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update = form.save(commit=False)
            update.linked_missing_person = report
            update.save()
            messages.success(request, "Update added to your case.")
            return redirect('family:report_detail', pk=pk)
    else:
        form = CaseUpdateForm()

    return render(request, 'family/add_case_update.html', {'form': form, 'report': report})


@family_required
def my_matches(request):
    """View all potential matches for family user's reports."""
    user = request.user

    # Get matches for all this user's reports (excluding ones they rejected)
    matches = MatchResult.objects.filter(
        missing_person__linked_family_user=user
    ).exclude(
        status='REJECTED'
    ).order_by('-confidence_score')

    # Mark notifications as read
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)

    return render(request, 'family/my_matches.html', {'matches': matches})


@family_required
def reject_match(request, pk):
    """Family user rejects a match (only for them; does not remove it globally)."""
    match = get_object_or_404(MatchResult, pk=pk, missing_person__linked_family_user=request.user)
    match.status = 'REJECTED'
    match.save()
    messages.info(request, "Match dismissed for your view. The case continues to be matched for others.")
    return redirect('family:my_matches')


@family_required
def close_case(request, pk):
    """Family user marks a case as FOUND or CLOSED."""
    report = get_object_or_404(MissingPerson, pk=pk, linked_family_user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'FOUND':
            report.status = 'FOUND'
            messages.success(request, f"{report.person_name} has been marked as found. We're glad!")
        elif action == 'CLOSED':
            report.status = 'CLOSED'
            messages.info(request, f"Case for {report.person_name} has been closed.")
        report.save()
        return redirect('family:archived_cases')

    return render(request, 'family/close_case.html', {'report': report})


@family_required
def archived_cases(request):
    """View resolved/closed cases."""
    cases = MissingPerson.objects.filter(
        linked_family_user=request.user
    ).exclude(status='ACTIVE')
    return render(request, 'family/archived_cases.html', {'cases': cases})
