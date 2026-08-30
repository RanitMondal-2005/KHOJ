from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps

from .models import MissingPerson, CaseUpdate
from .forms import MissingPersonForm, CaseUpdateForm
from matching.models import MatchResult
from notifications.models import Notification

# ---------------------- Custom Decorator to wrap family views with 2 checks (RBAC) --------------------------

def family_required(view_func): # view_func is a parameter representing the original Django view function that we put the decorator on top of. So,view_func holds the actual web page code that should only be executed if the user passes security checks.
    @login_required # CHECK 1 : User is logged in or not (if yes,then move to check 2)
    @wraps(view_func) # Identity Preservation : Ensures the original view function's metadata is preserved, beacuse Django sees every decorated view as wrapper — which can cause confusing error messages and makes stack traces much harder to read when something breaks.
    def wrapper(request, *args, **kwargs): # diff views have diff parameters so we use *args and **kwargs to smoothly handle them
        if request.user.role != 'FAMILY': # CHECK 2 : User is family or not
            messages.error(request, "Access denied. This section is for family users only.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

# ------------------------ Family Views ------------------------------------------------------------------

@family_required
def dashboard(request):
    """Family dashboard: overview of reports and matches."""
    user = request.user # extracting the current logged-in user
    active_reports = MissingPerson.objects.filter(linked_family_user=user, status='ACTIVE') # Fetches only THIS user's active reports
    recent_matches = MatchResult.objects.filter(
        missing_person__linked_family_user=user # Double underscore filter lookup — goes through MatchResult → missing_person → linked_family_user to find only matches belonging to this user's reports. 
    ).exclude(
        status='REJECTED' # Excludes dismissed matches
    ).order_by('-confidence_score')[:5] # [:5] — only top 5 for the dashboard preview. -confidence_score sorts highest score first.

    unread_count = Notification.objects.filter(user=user, is_read=False).count() # Badge number for the bell icon in navbar for unread notifications.

    context = {
        'active_reports': active_reports,
        'recent_matches': recent_matches,
        'active_count': active_reports.count(), # to give the frontend the number of active reports
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
            report.linked_family_user = user # Set the current user(who filled the report) as the owner to linked_family_user
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
def report_detail(request, pk): # pk-> primary key of the report,received via URL
    """View a single missing person report and its updates."""
    report = get_object_or_404(MissingPerson, pk=pk, linked_family_user=request.user) # linked_family_user=request.user to ensure ownership and prevent unauthorized access to other users' reports.(RBAC)
    updates = report.case_updates.all() # reverse foreign key lookup for all case updates of current report, For that we move: MissingPerson -> CaseUpdate, to fetch all related updates.
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
    report = get_object_or_404(MissingPerson, pk=pk, linked_family_user=request.user) # fetching which report the user is trying to update

    if report.status != 'ACTIVE':
        messages.warning(request, "Cannot add updates to a closed or resolved case.")
        return redirect('family:report_detail', pk=pk)

    if request.method == 'POST':
        form = CaseUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update = form.save(commit=False)
            update.linked_missing_person = report # updating the case update's linked_missing_person
            update.save()
            messages.success(request, "Update added to your case.")
            return redirect('family:report_detail', pk=pk)
    else:
        form = CaseUpdateForm()

    return render(request, 'family/add_case_update.html', {'form': form, 'report': report})

@family_required
def delete_case_update(request, pk):
    """
    Family user deletes one of their own case updates.
    Only POST allowed — no accidental deletions via GET.
    RBAC enforced — can only delete updates belonging to their own reports.
    """
    # Verify the Ownership first before deletion
    update = get_object_or_404(
        CaseUpdate,  # 1. Look in the CaseUpdate table...
        pk=pk,  # 2. Match the primary key
        linked_missing_person__linked_family_user=request.user  # 3. Follow the link to the parent report (linked_missing_person), then to its owner (linked_family_user), and check if it's ME (request.user)!
    )
    report_pk = update.linked_missing_person.pk  # Saving report_pk before deletion to get back to the report detail page after deletion

    if request.method == 'POST':  # Safety check: Only POST requests can delete updates
        update.delete()
        messages.success(request, "Update deleted.")

    return redirect('family:report_detail', pk=report_pk)  # Redirect back to the report detail page

@family_required
def my_matches(request):
    """View all potential matches for family user's reports."""
    user = request.user

    # Get matches for all this user's reports (excluding ones they rejected)
    matches = MatchResult.objects.filter(
        missing_person__linked_family_user=user # Go to the MatchResult model, look up the connected MissingPerson report, check if that report's linked_family_user matches our current logged-in user, and if it matches, return all MatchResult details for that user.
    ).exclude(
        status='REJECTED'
    ).order_by('-confidence_score')

    # Mark notifications as read
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)

    return render(request, 'family/my_matches.html', {'matches': matches})


@family_required
def reject_match(request, pk): # Removing a match from Potential Matches Section ("Dismiss Match" button in my_matches.html or report_detail.html)
    """Family user rejects a match (only for them; does not remove it globally)."""
    match = get_object_or_404(MatchResult, pk=pk, missing_person__linked_family_user=request.user) # Get the match object
    match.status = 'REJECTED'
    match.save()
    messages.info(request, "Match dismissed for your view. The case continues to be matched for others.")
    return redirect('family:my_matches')


@family_required
def close_case(request, pk):
    """Family user marks a case as FOUND or CLOSED. It will be archived."""
    report = get_object_or_404(MissingPerson, pk=pk, linked_family_user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action') # Get the action from the POST request(FOUND or CLOSED, which one the user selected & submitted via the form)
        if action == 'FOUND':
            report.status = 'FOUND'
            messages.success(request, f"{report.person_name} has been marked as found. We're glad!")
        elif action == 'CLOSED':
            report.status = 'CLOSED'
            messages.info(request, f"Case for {report.person_name} has been closed. Please contact support for further assistance.")
        report.save()
        return redirect('family:archived_cases')

    return render(request, 'family/close_case.html', {'report': report})


@family_required
def archived_cases(request):
    """View resolved/closed cases. Both Found and Closed Cases will be shown."""
    cases = MissingPerson.objects.filter(
        linked_family_user=request.user
    ).exclude(status='ACTIVE')
    return render(request, 'family/archived_cases.html', {'cases': cases})
