from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.contrib import messages
from django.db.models import Q

from family.models import MissingPerson
from hospital.models import UnidentifiedPatient
from matching.models import MatchResult
from accounts.models import HospitalProfile


def police_required(view_func):
    """Decorator: only police officers can access these views."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'POLICE':
            messages.error(request, "Access denied. This section is for police officers only.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@police_required
def dashboard(request):
    """Police dashboard overview."""
    user = request.user
    profile = user.police_profile
    district = profile.district

    # count unidentified patients in district (what hospitals reported)
    regional_patients = UnidentifiedPatient.objects.filter(
        district__iexact=district
    ).count()

    # count matches in district for quick overview
    regional_matches = MatchResult.objects.filter(
        Q(unidentified_patient__district__iexact=district)
    ).exclude(status='REJECTED').count()

    context = {
        'district': district,
        'regional_patients_count': regional_patients,
        'regional_matches_count': regional_matches,
        'police_station': profile.police_station_name,
    }
    return render(request, 'police/dashboard.html', context)


@police_required
def regional_cases(request):
    """
    Shows UNIDENTIFIED PATIENT RECORDS uploaded by hospitals in the officer's district.
    This is what police need - to know what unidentified persons are in their area.
    Search by estimated name or found location.
    """
    profile = request.user.police_profile
    district = profile.district

    # all patients (both UNIDENTIFIED and IDENTIFIED) in the district
    # police should see all, not just active ones
    patients = UnidentifiedPatient.objects.filter(
        Q(district__iexact=district) | Q(found_location__icontains=district)
    ).order_by('-admission_date')

    query = request.GET.get('q', '').strip()
    if query:
        patients = patients.filter(
            Q(estimated_name__icontains=query) |
            Q(found_location__icontains=query) |
            Q(district__icontains=query)
        )

    # status filter - default shows all, can filter by status
    status_filter = request.GET.get('status', '').strip()
    if status_filter in ('UNIDENTIFIED', 'IDENTIFIED'):
        patients = patients.filter(status=status_filter)

    return render(request, 'police/regional_cases.html', {
        'patients': patients,
        'district': district,
        'query': query,
        'status_filter': status_filter,
    })


@police_required
def case_detail(request, pk):
    """
    Full details of a hospital-uploaded unidentified patient record.
    Police see: all patient physical details, hospital contact, found location.
    Police do NOT see: family's personal details here.
    """
    patient = get_object_or_404(UnidentifiedPatient, pk=pk)
    profile = request.user.police_profile
    district = profile.district

    # soft warning if patient is outside their district
    out_of_jurisdiction = patient.district.lower() != district.lower()

    return render(request, 'police/case_detail.html', {
        'patient': patient,
        'out_of_jurisdiction': out_of_jurisdiction,
    })


@police_required
def nearby_matches(request):
    """
    Matched pairs (missing person ↔ unidentified patient) in officer's district.
    Police use this to identify cases worth following up on.
    """
    profile = request.user.police_profile
    district = profile.district

    matches = MatchResult.objects.filter(
        Q(missing_person__district__iexact=district) |
        Q(unidentified_patient__district__iexact=district)
    ).exclude(status='REJECTED').order_by('-confidence_score')

    return render(request, 'police/nearby_matches.html', {
        'matches': matches,
        'district': district,
    })


@police_required
def search_hospitals(request):
    """Hospital directory for police to find contact info in their district."""
    profile = request.user.police_profile
    district = profile.district

    hospitals = HospitalProfile.objects.filter(district__iexact=district)

    query = request.GET.get('q', '').strip()
    if query:
        hospitals = HospitalProfile.objects.filter(
            Q(hospital_name__icontains=query) |
            Q(district__icontains=query)
        )

    return render(request, 'police/search_hospitals.html', {
        'hospitals': hospitals,
        'district': district,
        'query': query,
    })


@police_required
def archived_cases(request):
    """
    Resolved/identified patients in the officer's district.
    Historical reference during investigations.
    """
    profile = request.user.police_profile
    district = profile.district

    cases = UnidentifiedPatient.objects.filter(
        Q(district__iexact=district),
        status='IDENTIFIED'
    )

    query = request.GET.get('q', '').strip()
    if query:
        cases = cases.filter(estimated_name__icontains=query)

    return render(request, 'police/archived_cases.html', {
        'cases': cases,
        'district': district,
        'query': query,
    })