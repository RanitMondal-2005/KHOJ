"""
accounts/forms.py

Registration forms for all 3 roles + separate login forms per role.
Family logs in with email, Hospital with staff_id, Police with police_id.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import KhojUser, HospitalProfile, PoliceProfile


# ── FAMILY REGISTRATION ────────────────────────────────────────────────────────

class FamilyRegistrationForm(forms.ModelForm):

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
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if KhojUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'FAMILY'
        if commit:
            user.save()
        return user


# ── HOSPITAL REGISTRATION ──────────────────────────────────────────────────────

class HospitalRegistrationForm(forms.Form):

    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    staff_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Unique staff ID issued by your hospital"
    )
    hospital_registration_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Hospital registration number (stored for records)"
    )
    hospital_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    district = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    emergency_contact = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    hospital_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if KhojUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_staff_id(self):
        staff_id = self.cleaned_data.get('staff_id')
        if HospitalProfile.objects.filter(staff_id=staff_id).exists():
            raise forms.ValidationError("This Staff ID is already registered.")
        return staff_id

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
            role='HOSPITAL', password=d['password'],
        )
        HospitalProfile.objects.create(
            user=user, staff_id=d['staff_id'],
            hospital_registration_id=d['hospital_registration_id'],
            hospital_name=d['hospital_name'], district=d['district'],
            address=d['address'], emergency_contact=d['emergency_contact'],
            hospital_email=d['hospital_email'],
        )
        return user


# ── POLICE REGISTRATION ────────────────────────────────────────────────────────

class PoliceRegistrationForm(forms.Form):

    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    police_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Your unique police officer ID"
    )
    police_station_registration_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Police station registration number (for records)"
    )
    police_station_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    district = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if KhojUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_police_id(self):
        police_id = self.cleaned_data.get('police_id')
        if PoliceProfile.objects.filter(police_id=police_id).exists():
            raise forms.ValidationError("This Police ID is already registered.")
        return police_id

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
            police_station_registration_id=d['police_station_registration_id'],
            police_station_name=d['police_station_name'], district=d['district'],
        )
        return user


# ── LOGIN FORMS (one per role) ─────────────────────────────────────────────────

class KhojLoginForm(AuthenticationForm):
    """Family login form - email + password."""
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


class HospitalLoginForm(forms.Form):
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