"""
hospital/views.py

Views for hospital staff.
Hospital staff can only view/manage their own hospital's records.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.contrib import messages

from .models import UnidentifiedPatient
from .forms import UnidentifiedPatientForm
from matching.models import MatchResult
from notifications.models import Notification

# ---------------- Custom Decorator For Hospital views with 2 checks (RBAC) ----------------

def hospital_required(view_func): # # view_func is a parameter representing the original Django view function that we put the decorator on top of. So,view_func holds the actual web page code that should only be executed if the both checks are passed
    """Decorator to restrict view to hospital staff only."""
    @login_required # Check 1 :
    @wraps(view_func) # Identity Preservation : Preserving MetaData (like __name__, __doc__, __module__): it copies metadata from view_func onto wrapper first. Without this, Django sees every decorated view as wrapper — which can cause confusing error messages and makes stack traces much harder to read when something breaks.
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'HOSPITAL': # Check 2:
            messages.error(request, "Access denied. This section is for hospital staff only.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

# ---------------------- Hospital Views ----------------------------------------------------------

@hospital_required
def dashboard(request):
    """Hospital dashboard: overview of patients and matches."""
    user = request.user
    active_patients = UnidentifiedPatient.objects.filter(linked_hospital=user, status='UNIDENTIFIED')
    recent_matches = MatchResult.objects.filter(
        unidentified_patient__linked_hospital=user
    ).exclude(status='REJECTED').order_by('-confidence_score')[:5]

    context = {
        'active_patients': active_patients,
        'active_count': active_patients.count(),
        'recent_matches': recent_matches,
    }
    return render(request, 'hospital/dashboard.html', context)


@hospital_required
def add_patient(request):
    """Upload a new unidentified patient record."""
    if request.method == 'POST':
        form = UnidentifiedPatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.linked_hospital = request.user
            patient.save()
            messages.success(request, "Patient record uploaded. Matching will run automatically.")
            return redirect('hospital:view_patients')
    else:
        form = UnidentifiedPatientForm()

    return render(request, 'hospital/add_patient.html', {'form': form})


@hospital_required
def view_patients(request):
    """View all active (unidentified) patients from this hospital."""
    patients = UnidentifiedPatient.objects.filter(
        linked_hospital=request.user, status='UNIDENTIFIED'
    )
    return render(request, 'hospital/view_patients.html', {'patients': patients})


@hospital_required
def patient_detail(request, pk):
    """View details of a specific patient record."""
    patient = get_object_or_404(UnidentifiedPatient, pk=pk, linked_hospital=request.user)
    matches = MatchResult.objects.filter(unidentified_patient=patient).exclude(status='REJECTED').order_by('-confidence_score')

    context = {
        'patient': patient,
        'matches': matches,
    }
    return render(request, 'hospital/patient_detail.html', context)

@hospital_required
def match_alerts(request):
    """View all potential matches for hospital's patients."""
    # Mark notifications as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    matches = MatchResult.objects.filter(
        unidentified_patient__linked_hospital=request.user
    ).exclude(status='REJECTED').order_by('-confidence_score')

    return render(request, 'hospital/match_alerts.html', {'matches': matches})


@hospital_required
def reject_match(request, pk):
    """Hospital staff dismisses a match (only for their view)."""
    match = get_object_or_404(MatchResult, pk=pk, unidentified_patient__linked_hospital=request.user)
    match.status = 'REJECTED'
    match.save()
    messages.info(request, "Match dismissed. The case continues to be visible to other parties.")
    return redirect('hospital:match_alerts')


@hospital_required
def mark_identified(request, pk):
    patient = get_object_or_404(UnidentifiedPatient, pk=pk, linked_hospital=request.user)

    if request.method == 'POST':
        patient.status = 'IDENTIFIED'
        patient.save()

        # delete all match results for this patient — identified, no longer needs matching
        from matching.models import MatchResult
        MatchResult.objects.filter(unidentified_patient=patient).delete()

        messages.success(request, "Patient marked as identified. Record moved to resolved section.")
        return redirect('hospital:resolved_patients')

    return render(request, 'hospital/confirm_identify.html', {'patient': patient})


@hospital_required
def resolved_patients(request):
    """
    View all identified patients.
    Has a simple name search filter so hospital can find a specific resolved patient.
    """
    # retrieve only records belonging to the current hospital that have been resolved
    patients = UnidentifiedPatient.objects.filter(
        linked_hospital=request.user, status='IDENTIFIED'
    )

    query = request.GET.get('q', '').strip() # bringing {'q':...}, that value typed by user in the input field of the form;which defaults to '' if empty-no name typed
    show_unnamed = request.GET.get('unnamed', '') # when unknown patients button is clicked our hardcoded url in <a> tag runs and we get the 1 value here(since .../?unnamed=1) - indicating we need to show all patients with empty str names stored in DB

    if show_unnamed: # '1' is truthy value, so we got the indication then filter..if '' empty str then this if would be false & no filter for this
        # filter only patients with no name stored
        patients = patients.filter(estimated_name='')
    elif query: # else: bring the name and see if that matches
        patients = patients.filter(estimated_name__icontains=query)

    return render(request, 'hospital/resolved_patients.html', {
        'patients': patients,
        'query': query, # Sent back the typed name value to HTML context to Preserve user input in search box on reload
        'show_unnamed': show_unnamed, # passed back to the template, turning the button solid yellow or toggle btw
    })