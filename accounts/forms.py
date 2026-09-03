"""
accounts/forms.py

Registration forms for all 3 roles + separate login forms per role.
Family logs in with email, Hospital with staff_id, Police with police_id.
"""

import re # for regex patterns check
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from .models import KhojUser, HospitalProfile, PoliceProfile

# ── REGISTRATION FORMS ───────────────────────────────────────────────────────

# ── FAMILY REGISTRATION ──────

class FamilyRegistrationForm(forms.ModelForm):
    # Generating all the necessary fields for family registration form acc to our requirements
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = KhojUser
        fields = ['full_name', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name', 'maxlength': '150'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

    # Validating name
    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if not name:
            raise forms.ValidationError("Full name is required.")
        if len(name) < 2:
            raise forms.ValidationError("Full name must be at least 2 characters long.")
        if not re.match(r"^[A-Za-z\s.'-]+$", name):
            raise forms.ValidationError("Name should only contain letters, spaces, hyphens, apostrophes, or periods.")
        return name

    # Validating email uniqueness
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if KhojUser.objects.filter(email=email).exists(): # checking if email is already in use(that is, if a user with this email already exists in our backend DB)
            raise forms.ValidationError("An account with this email already exists.")
        return email

    # Validating password complexity
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password) # Triggers Django's settings.AUTH_PASSWORD_VALIDATORS (min length, common passwords, etc.)
        return password

    # Validating password confirmation (Since this form is not using Django's built-in user creation form, we need to manually check password confirmation)
    def clean(self):
        cleaned_data = super().clean() # Call the parent class's (which is ModelForm) clean method to ensure all fields are validated
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    # Saving the user instance in our DB
    def save(self, commit=True):
        user = super().save(commit=False) # commit=False -> not saving the user instance to the DB yet before our password hashing
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password']) # Hashing the password(by set_password(..)), because we need to store it securely to avoid plain text storage directly in the DB
        user.role = 'FAMILY'
        if commit:
            user.save() # Saving the user to the DB
        return user


# ── HOSPITAL REGISTRATION ──────────────

class HospitalRegistrationForm(forms.Form): 
    # plain forms.Form is used for hospital and police registration but for family we are using ModelForm, because ModelForm can target only 1 model at a time but for hospital and police we need to handle 2 diff DB tables : 1 to store personal user info and 1 to store profile info

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
        if not re.match(r"^[A-Za-z\s.'-]+$", name):
            raise forms.ValidationError("Name should only contain letters, spaces, hyphens, apostrophes, or periods.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if KhojUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_staff_id(self):
        staff_id = self.cleaned_data.get('staff_id', '').strip()
        if not staff_id:
            raise forms.ValidationError("Staff ID is required.")
        if not re.match(r"^[A-Za-z0-9\-_/]+$", staff_id):
            raise forms.ValidationError("Staff ID can only contain letters, numbers, hyphens, underscores, or slashes.")
        if HospitalProfile.objects.filter(staff_id=staff_id).exists():
            raise forms.ValidationError("This Staff ID is already registered.")
        return staff_id

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
        user = KhojUser.objects.create_user( # first save staff personal details to user table (i.e, our base KhojUser model)
            email=d['email'], full_name=d['full_name'],
            role='HOSPITAL', password=d['password'],
        )
        HospitalProfile.objects.create( # then save other details to profile table (i.e, HospitalProfile model) for separate institutional fields
            user=user, staff_id=d['staff_id'],
            hospital_registration_id=d['hospital_registration_id'].strip(),
            hospital_name=d['hospital_name'].strip(), district=d['district'].strip(),
            address=d['address'].strip(), emergency_contact=d['emergency_contact'],
            hospital_email=d['hospital_email'].strip().lower(),
        )
        return user


# ── POLICE REGISTRATION ────────────────────

class PoliceRegistrationForm(forms.Form):

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
        if not re.match(r"^[A-Za-z\s.'-]+$", name):
            raise forms.ValidationError("Name should only contain letters, spaces, hyphens, apostrophes, or periods.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if KhojUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_police_id(self):
        police_id = self.cleaned_data.get('police_id', '').strip()
        if not police_id:
            raise forms.ValidationError("Police ID is required.")
        if not re.match(r"^[A-Za-z0-9\-_/]+$", police_id):
            raise forms.ValidationError("Police ID can only contain letters, numbers, hyphens, underscores, or slashes.")
        if PoliceProfile.objects.filter(police_id=police_id).exists():
            raise forms.ValidationError("This Police ID is already registered.")
        return police_id

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
        user = KhojUser.objects.create_user(
            email=d['email'], full_name=d['full_name'],
            role='POLICE', password=d['password'],
        )
        PoliceProfile.objects.create(
            user=user, police_id=d['police_id'],
            police_station_registration_id=d['police_station_registration_id'].strip(),
            police_station_name=d['police_station_name'].strip(), district=d['district'].strip(),
        )
        return user


# ── LOGIN FORMS (one per role) ─────────────────────────────────────────────────

# ----- Family login form -----

class KhojLoginForm(AuthenticationForm):  # Authentication form is the built-in Django form that we extended acc to our need.
    # AuthenticationForm automatically creates Username and Password fields for you & does the authentication by default
    """Family login form - email + password."""
    username = forms.EmailField(    # We override the username field to use email instead of the default username.
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'your@email.com',
            'autofocus': True
        })
    )
    password = forms.CharField(  # We override the password field to use a custom widget.
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password'
        })
    )

# ----- Hospital login form -----
class HospitalLoginForm(forms.Form):  # By inheriting forms.Form -> we are starting with a completely blank canvas for a form, where we will design the fields manually.
    """Hospital staff login - staff_id + password."""
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
    """Police login - police_id + password."""
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