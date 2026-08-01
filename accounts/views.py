"""
accounts/views.py

Registration, login, logout, and dashboard redirect views.
Login :
Each role uses a different identifier to log in:
  Family   -> email + password
  Hospital -> staff_id + password
  Police   -> police_id + password

Registration :
 Family users will see -> the FamilyRegistrationForm,
 hospital staff will see -> the HospitalRegistrationForm, 
 police officers will see -> the PoliceRegistrationForm.

"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import (
    FamilyRegistrationForm,
    HospitalRegistrationForm,
    PoliceRegistrationForm,
    KhojLoginForm,
    HospitalLoginForm,
    PoliceLoginForm,
)

# --- Home page ----
def home(request):
    factors = [
        'Gender', 'Blood Group', 'Age Range', 'Height', 'Weight',
        'District', 'Eye Color', 'Hair Color', 'Skin Tone',
        'Identifying Marks', 'Clothing', 'Photo Similarity'
    ]
    return render(request, 'accounts/home.html', {'factor_list': factors})

# ---- About Us page ----
def about(request):
    return render(request, 'accounts/about.html')

# ---- Registration choice page ----
def register_choice(request):
    """User picks which role they are before seeing the registration form."""
    return render(request, 'accounts/register_choice.html')

# ---- Login choice page ----
def login_choice(request):
    """Landing page where user picks which login page to go to."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/login_choice.html')

# --------------------- LOGIN PAGES --------------------- :

# ----- Family login ----
def login_family(request):
    """Family login - uses email + password."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = KhojLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role != 'FAMILY':
                messages.error(request, "This login page is for family users only.")
                return redirect('login_family')
            # backend must be specified when multiple backends are configured
            login(request, user, backend='accounts.backends.EmailBackend') # backend='accounts.backends.EmailBackend' means we are using the EmailBackend for authentication, this is imp to specify because multiple backends like StaffIDBackend and PoliceIDBackend etc. are configured.
            messages.success(request, f"Welcome back, {user.full_name}!")
            return redirect('family:dashboard')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = KhojLoginForm()

    return render(request, 'accounts/login_family.html', {'form': form})

# ---- Hospital login ----
def login_hospital(request):
    """Hospital login - uses staff_id + password."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = HospitalLoginForm(request.POST)
        if form.is_valid():
            staff_id = form.cleaned_data['staff_id']
            password = form.cleaned_data['password']

            # StaffIDBackend handles the lookup by staff_id
            user = authenticate(request, username=staff_id, password=password)

            if user and user.role == 'HOSPITAL':
                login(request, user, backend='accounts.backends.StaffIDBackend')
                messages.success(request, f"Welcome back, {user.full_name}!")
                return redirect('hospital:dashboard')
            else:
                messages.error(request, "Invalid Staff ID or password.")
    else:
        form = HospitalLoginForm()

    return render(request, 'accounts/login_hospital.html', {'form': form})

# --- Police login ---
def login_police(request):
    """Police login - uses police_id + password."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = PoliceLoginForm(request.POST)
        if form.is_valid():
            police_id = form.cleaned_data['police_id']
            password = form.cleaned_data['password']

            # PoliceIDBackend handles the lookup by police_id
            user = authenticate(request, username=police_id, password=password)

            if user and user.role == 'POLICE':
                login(request, user, backend='accounts.backends.PoliceIDBackend')
                messages.success(request, f"Welcome back, {user.full_name}!")
                return redirect('police:dashboard')
            else:
                messages.error(request, "Invalid Police ID or password.")
    else:
        form = PoliceLoginForm()

    return render(request, 'accounts/login_police.html', {'form': form})


# ---- Logout view ----
# NOTE : We're using Django's logout() function (imported at the top), but wrapping it in our own view to add the flash message for UI improvements.
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


# --------------------- REGISTRATION  PAGES --------------------- :

# --- Family registration ---
def register_family(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = FamilyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # must specify backend explicitly - multiple backends are configured
            login(request, user, backend='accounts.backends.EmailBackend')
            messages.success(request, f"Welcome to Khoj, {user.full_name}!")
            return redirect('family:dashboard')
    else:
        form = FamilyRegistrationForm()

    return render(request, 'accounts/register_family.html', {'form': form})

# --- Hospital registration ---
def register_hospital(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='accounts.backends.EmailBackend')
            messages.success(request, f"Welcome to Khoj, {user.full_name}!")
            return redirect('hospital:dashboard')
    else:
        form = HospitalRegistrationForm()

    return render(request, 'accounts/register_hospital.html', {'form': form})

# --- Police registration ---
def register_police(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = PoliceRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='accounts.backends.EmailBackend')
            messages.success(request, f"Welcome to Khoj, {user.full_name}!")
            return redirect('police:dashboard')
    else:
        form = PoliceRegistrationForm()

    return render(request, 'accounts/register_police.html', {'form': form})

# --- Dashboard redirect according to user role ---
@login_required
def dashboard_redirect(request):
    """Sends logged-in user to their role-specific dashboard."""
    user = request.user
    if user.role == 'FAMILY':
        return redirect('family:dashboard')
    elif user.role == 'HOSPITAL':
        return redirect('hospital:dashboard')
    elif user.role == 'POLICE':
        return redirect('police:dashboard')
    return redirect('home')