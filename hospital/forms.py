"""
hospital/forms.py

UnidentifiedPatientForm - For Hospital Staff Members
"""

import re
from django import forms
from .models import UnidentifiedPatient
from datetime import date as dt_date

class UnidentifiedPatientForm(forms.ModelForm):

    class Meta:
        model = UnidentifiedPatient
        exclude = ['linked_hospital', 'status', 'created_at', 'updated_at']
        widgets = {
            'estimated_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank if completely unknown',
                'maxlength': '150',
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated age',
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated height',
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated weight',
            }),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'eye_color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Brown',
                'maxlength': '50',
            }),
            'hair_color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Black',
                'maxlength': '50',
            }),
            'skin_tone': forms.Select(attrs={'class': 'form-select'}),
            'identifying_marks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Scars, tattoos, birthmarks, medical marks...',
                'maxlength': '500',
            }),
            'clothing_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g. Blue shirt, black trousers, brown sandals...',
                'maxlength': '700',
            }),
            'found_id_type': forms.Select(attrs={'class': 'form-select'}),
            'found_id_last4': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last 4 digits only',
                'maxlength': '4',
            }),
            'found_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Near Sealdah Railway Station Platform 4',
                'maxlength': '255',
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. North 24 Parganas',
                'maxlength': '100',
            }),
            'condition_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Physical condition, injuries, consciousness state...',
                'maxlength': '1000',
            }),
            'admission_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'max': dt_date.today().isoformat(),
            }),
        }

    # ------- Server-Side Field Cleaners -------

    def clean_estimated_name(self):
        name = self.cleaned_data.get('estimated_name', '').strip()
        if name and not re.match(r"^[A-Za-z\s.'-]+$", name):
            raise forms.ValidationError("Name should only contain letters, spaces, hyphens, apostrophes, or periods.")
        return name

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None:
            raise forms.ValidationError("Estimated age is required.")
        if age < 1 or age > 100:
            raise forms.ValidationError("Estimated age must be between 1 and 100.")
        return age

    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height is None:
            raise forms.ValidationError("Height is required.")
        if height < 30 or height > 250:
            raise forms.ValidationError("Height must be between 30 cm and 250 cm.")
        return height

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is None:
            raise forms.ValidationError("Weight is required.")
        if weight < 1 or weight > 300:
            raise forms.ValidationError("Weight must be between 1 kg and 300 kg.")
        return weight

    def clean_found_location(self):
        location = self.cleaned_data.get('found_location', '').strip()
        if not location:
            raise forms.ValidationError("Found location is required.")
        if len(location) < 3:
            raise forms.ValidationError("Found location must be at least 3 characters long.")
        if not re.match(r"^[A-Za-z0-9\s.,#'\-/]+$", location):
            raise forms.ValidationError("Location contains invalid characters.")
        return location

    def clean_district(self):
        district = self.cleaned_data.get('district', '').strip()
        if not district:
            raise forms.ValidationError("District is required.")
        if len(district) < 2:
            raise forms.ValidationError("District name must be at least 2 characters long.")
        if not re.match(r"^[A-Za-z0-9\s.'-]+$", district):
            raise forms.ValidationError("District can only contain letters, numbers, spaces, periods, apostrophes, or hyphens.")
        return district

    def clean_admission_date(self):
        date = self.cleaned_data.get('admission_date')
        if not date:
            raise forms.ValidationError("Admission date is required.")
        if date > dt_date.today():
            raise forms.ValidationError("Admission date cannot be in the future.")
        return date

    # ------- Cross-Field Validation (ID Check) -------

    def clean(self):
        cleaned_data = super().clean()
        id_type = cleaned_data.get('found_id_type', '').strip()
        last4 = cleaned_data.get('found_id_last4', '').strip()

        # If ID type chosen, 4 digits are mandatory
        if id_type and not last4:
            self.add_error('found_id_last4', "Please enter the last 4 digits of the ID.")
        
        # If 4 digits typed, ID type is mandatory
        if last4 and not id_type:
            self.add_error('found_id_type', "Please select the ID type for these 4 digits.")

        # Ensure last 4 digits are strictly 4 digits
        if last4:
            if not last4.isdigit() or len(last4) != 4:
                self.add_error('found_id_last4', "Must be exactly 4 digits.")

        return cleaned_data