"""
accounts/forms.py

Registration forms for all 3 roles + separate login forms per role.
- Family Registration: Uses ModelForm since it only writes to KhojUser.
- Hospital & Police Registration: Uses forms.Form because each saves into TWO tables:
  1. KhojUser (Base credentials: email, password, role)
  2. HospitalProfile / PoliceProfile (Institutional fields: IDs, station/hospital details, district)
- Login Forms: Separate forms tailored to each role's primary login credential (Email, Staff ID, Police ID).
"""

import re  # For regex validation (names, IDs, district formats)
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from .models import KhojUser, HospitalProfile, PoliceProfile

# ── REGISTRATION FORMS ───────────────────────────────────────────────────────

# ── FAMILY REGISTRATION ──────

class FamilyRegistrationForm(forms.ModelForm):
    # ModelForm targets KhojUser directly. Password fields are declared explicitly to add styling and confirm check.
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta: # Class Meta inside ModelForm controls how the form interacts with a database model
        model = KhojUser
        fields = ['full_name', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name', 'maxlength': '150'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if not name:
            raise forms.ValidationError("Full name is required.")
        if len(name) < 2:
            raise forms.ValidationError("Full name must be at least 2 characters long.")
        if not re.match(r"^[A-Za-z\s.'-]+$", name):
            raise forms.ValidationError("Name should only contain letters, spaces, hyphens, apostrophes, or periods.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        # Verify email uniqueness before proceeding to user creation
        if KhojUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Triggers Django's settings.AUTH_PASSWORD_VALIDATORS (min length, common passwords, numeric rules)
            validate_password(password)
        return password

    def clean(self):
        # Cross-field validation: confirms both passwords match exactly
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        # commit=False allows password hashing and role assignment before saving to database
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])  # Hashes the plain text password securely
        user.role = 'FAMILY'
        if commit:
            user.save()
        return user


# ── HOSPITAL REGISTRATION ──────────────

class HospitalRegistrationForm(forms.Form):
    # Plain forms.Form is used because this registration splits inputs across TWO models (KhojUser and HospitalProfile) and ModelForm can target only 1 model at a time.

    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Staff Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Personal/Login Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    staff_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. HOSP-104'}),
        help_text="Unique staff ID issued by your hospital"
    )
    hospital_registration_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. REG-WB-2024-09'}),
        help_text="Hospital registration number (stored for records)"
    )
    hospital_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital Name'}))
    district = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'District'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Hospital Address'}))
    emergency_contact = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit Emergency Contact'}))
    hospital_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Official Hospital Email'}))

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if not name:
            raise forms.ValidationError("Staff full name is required.")
        if len(name) < 2:
            raise forms.ValidationError("Staff full name must be at least 2 characters long.")
        if not re.match(r"^[A-Za-z\s.'-]+$", name):
            raise forms.ValidationError("Name should only contain letters, spaces, hyphens, apostrophes, or periods.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if KhojUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_staff_id(self):
        staff_id = self.cleaned_data.get('staff_id', '').strip()
        if not staff_id:
            raise forms.ValidationError("Staff ID is required.")
        if len(staff_id)<2:
            raise forms.ValidationError("Staff ID should be more than two characters.")
        if not re.match(r"^[A-Za-z0-9\-_/]+$", staff_id):
            raise forms.ValidationError("Staff ID can only contain letters, numbers, hyphens, underscores, or slashes.")
        if HospitalProfile.objects.filter(staff_id=staff_id).exists():
            raise forms.ValidationError("This Staff ID is already registered.")
        return staff_id

    def clean_hospital_registration_id(self):
        reg_id = self.cleaned_data.get('hospital_registration_id', '').strip()
        if not reg_id:
            raise forms.ValidationError("Hospital registration ID is required.")
        if len(reg_id)<2:
            raise forms.ValidationError("Hospital Registration ID is too Small.")
        return reg_id

    def clean_hospital_name(self):
        name = self.cleaned_data.get('hospital_name', '').strip()
        if not name:
            raise forms.ValidationError("Hospital name is required.")
        if len(name) < 3:
            raise forms.ValidationError("Hospital name must be at least 3 characters.")
        # Permits numbers, dots, hyphens, and brackets for multi-unit hospitals
        if not re.match(r"^[A-Za-z0-9\s.,'()/-]+$", name):
            raise forms.ValidationError("Hospital name contains invalid special characters.")
        return name

    def clean_district(self):
        district = self.cleaned_data.get('district', '').strip()
        if not district:
            raise forms.ValidationError("District is required.")
        if len(district) < 2:
            raise forms.ValidationError("District name must be at least 2 characters.")
        if not re.match(r"^[A-Za-z0-9\s.'-]+$", district):
            raise forms.ValidationError("District contains invalid characters.")
        return district.title() # Standadize district eg:"Kolkata" -> "kolkata"

    def clean_address(self):
        address = self.cleaned_data.get('address', '').strip()
        if not address:
            raise forms.ValidationError("Hospital address is required.")
        return address

    def clean_emergency_contact(self):
        contact = self.cleaned_data.get('emergency_contact', '').strip()
        if not contact:
            raise forms.ValidationError("Emergency contact number is required.")
        if not contact.isdigit():
            raise forms.ValidationError("Emergency contact must contain digits only.")
        if len(contact) != 10:
            raise forms.ValidationError("Emergency contact must be exactly 10 digits.")
        return contact

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self):
        d = self.cleaned_data
        # 1. Create base auth user record in KhojUser table
        user = KhojUser.objects.create_user(
            email=d['email'],
            full_name=d['full_name'],
            role='HOSPITAL',
            password=d['password'],
        )
        # 2. Create linked profile record in HospitalProfile table
        HospitalProfile.objects.create(
            user=user,
            staff_id=d['staff_id'],
            hospital_registration_id=d['hospital_registration_id'],
            hospital_name=d['hospital_name'],
            district=d['district'],
            address=d['address'],
            emergency_contact=d['emergency_contact'],
            hospital_email=d['hospital_email'].strip().lower(),
        )
        return user


# ── POLICE REGISTRATION ────────────────────

class PoliceRegistrationForm(forms.Form):
    # Plain forms.Form used to handle simultaneous creation of KhojUser + PoliceProfile as ModeForm Can only target 1 model at a time.

    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Officer Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Official / Login Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    police_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. POL-5542'}),
        help_text="Your unique police officer ID"
    )
    police_station_registration_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. PS-REG-981'}),
        help_text="Police station registration number (for records)"
    )
    police_station_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Police Station Name'}))
    district = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'District'}))

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if not name:
            raise forms.ValidationError("Officer full name is required.")
        if len(name) < 2:
            raise forms.ValidationError("Officer full name must be at least 2 characters long.")
        if not re.match(r"^[A-Za-z\s.'-]+$", name):
            raise forms.ValidationError("Name should only contain letters, spaces, hyphens, apostrophes, or periods.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if KhojUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_police_id(self):
        police_id = self.cleaned_data.get('police_id', '').strip()
        if not police_id:
            raise forms.ValidationError("Police ID is required.")
        if len(police_id)<3:
            raise forms.ValidationError('Police ID is too short.')
        if not re.match(r"^[A-Za-z0-9\-_/]+$", police_id):
            raise forms.ValidationError("Police ID can only contain letters, numbers, hyphens, underscores, or slashes.")
        if PoliceProfile.objects.filter(police_id=police_id).exists():
            raise forms.ValidationError("This Police ID is already registered.")
        return police_id

    def clean_police_station_name(self):
        station = self.cleaned_data.get('police_station_name', '').strip()
        if not station:
            raise forms.ValidationError("Police station name is required.")
        if len(station) < 3:
            raise forms.ValidationError("Police station name must be at least 3 characters.")
        # Permits numbers, spaces, and punctuation for divisions (e.g. "Sector-V PS", "Division 2")
        if not re.match(r"^[A-Za-z0-9\s.,'()/-]+$", station):
            raise forms.ValidationError("Station name contains invalid special characters.")
        return station

    def clean_police_station_registration_id(self):
        reg_id = self.cleaned_data.get('police_station_registration_id', '').strip()
        if not reg_id:
            raise forms.ValidationError("Police station registration ID is required.")
        if len(reg_id)<3:
            raise forms.ValidationError("Station Registration ID is too Short.")
        if not re.match(r"^[A-Za-z0-9\-_/]+$", reg_id):
            raise forms.ValidationError("Registration ID can only contain letters, numbers, hyphens, underscores, or slashes.")
        return reg_id

    def clean_district(self):
        district = self.cleaned_data.get('district', '').strip()
        if not district:
            raise forms.ValidationError("District is required.")
        if len(district) < 2:
            raise forms.ValidationError("District name must be at least 2 characters.")
        # Allows digits to support districts like "North 24 Parganas"
        if not re.match(r"^[A-Za-z0-9\s.'-]+$", district):
            raise forms.ValidationError("District contains invalid characters.")
        # Standardize title case so case searches cross-match reliably (e.g. "north 24 parganas" -> "North 24 Parganas")
        return district.title()

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self):
        d = self.cleaned_data
        # 1. Create base auth user record in KhojUser table
        user = KhojUser.objects.create_user(
            email=d['email'],
            full_name=d['full_name'],
            role='POLICE',
            password=d['password'],
        )
        # 2. Create linked profile record in PoliceProfile table
        PoliceProfile.objects.create(
            user=user,
            police_id=d['police_id'],
            police_station_registration_id=d['police_station_registration_id'],
            police_station_name=d['police_station_name'],
            district=d['district'],
        )
        return user


# ── LOGIN FORMS (one per role) ─────────────────────────────────────────────────

# ----- Family login form -----

class KhojLoginForm(AuthenticationForm):
    """
    Family login form (Email + Password).
    Inherits Django's built-in AuthenticationForm. We override 'username' to display as an Email field,
    while internally Django passes it to EmailBackend for authentication.
    """
    username = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'your@email.com',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password'
        })
    )


# ----- Hospital login form -----

class HospitalLoginForm(forms.Form):
    """
    Hospital staff login (Staff ID + Password).
    Explicit form capturing staff_id instead of email.
    The view passes staff_id into authenticate(username=staff_id) in views.py, which routes to StaffIDBackend.
    """
    staff_id = forms.CharField(
        label="Staff ID",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'e.g. STAFF001',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password'
        })
    )

    def clean_staff_id(self):
        return self.cleaned_data.get('staff_id', '').strip()


# ----- Police login form -----

class PoliceLoginForm(forms.Form):
    """
    Police officer login (Police ID + Password).
    Explicit form capturing police_id instead of email.
    The view passes police_id into authenticate(username=police_id) in views.py, which routes to PoliceIDBackend.
    """
    police_id = forms.CharField(
        label="Police Officer ID",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'e.g. WB001234',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password'
        })
    )

    def clean_police_id(self):
        return self.cleaned_data.get('police_id', '').strip()
