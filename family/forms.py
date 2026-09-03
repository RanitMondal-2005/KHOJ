"""
family/forms.py

MissingPersonForm - For Family Members
"""

import re # Python's built-in module for working with regex
from django import forms
from .models import MissingPerson, CaseUpdate


class MissingPersonForm(forms.ModelForm):

    class Meta:
        model = MissingPerson
        exclude = ['linked_family_user', 'status', 'created_at', 'updated_at', 'contact_number'] # We exclude fields that are either set automatically by the system (linked_family_user, status, timestamps), handled by Django itself (auto_now fields).
        widgets = {
            'person_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name',
                'maxlength': '150',
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'cm',
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'kg',
            }),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'eye_color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Brown',
                'maxlength': '15',
            }),
            'hair_color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Black',
                'maxlength': '15',
            }),
            'skin_tone': forms.Select(attrs={'class': 'form-select'}),
            'identifying_marks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3, # rows will ensure initially upto 3 rows are visible when form is first loaded
                'placeholder': 'Scars, tattoos, birthmarks...',
                'maxlength': '500',
            }),
            'clothing_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Last known clothing...',
                'maxlength': '700',
            }),
            'aadhaar_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12-digit Aadhaar number',
                'maxlength': '12',
            }),
            'relation': forms.Select(attrs={'class': 'form-select'}),
            'filer_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your 10-digit contact number',
                'maxlength': '10',
            }),
            'filer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email (optional)',
            }),
            'last_seen_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Near City Metro Station, Gate No. 2',
                'maxlength': '150',
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. North 24 Parganas',
                'maxlength': '50',
            }),
            'last_seen_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'fir_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional (e.g., 124/2026)',
                'maxlength': '30',
            }),
            'police_station_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional (e.g., Central Police Station)',
                'maxlength': '100',
            }),
        }

    # ------- Server Side Validation for restricting age, height, weight & Aadhaar & Contact No ---------

    # VALIDATION 1: person_name: only letters, spaces, hyphens, apostrophes, periods
    def clean_person_name(self):
        name = self.cleaned_data.get('person_name', '').strip()
        if not name:
            raise forms.ValidationError("Person name is required.")
        if not re.match(r"^[A-Za-z\s.'-]+$", name):
            raise forms.ValidationError("Name should only contain letters, spaces, hyphens, apostrophes, or periods.")
        return name

    # VALIDATION 2 : age: must be between 1 and 100, no decimals and no negatives
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None:
            raise forms.ValidationError("Age is required.")
        if age < 1 or age > 100:
            raise forms.ValidationError("Age must be between 1 and 100.")
        return age

    # VALIDATION 3 : height: between 30 cm (infant) and 250 cm (adult)
    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height is None:
            raise forms.ValidationError("Height is required.")
        if height < 30 or height > 250:
            raise forms.ValidationError("Height must be between 30 cm and 250 cm.")
        return height

    # VALIDATION 4 : weight: between 1 kg (infant) and 300 kg (adult)
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is None:
            raise forms.ValidationError("Weight is required.")
        if weight < 1 or weight > 300:
            raise forms.ValidationError("Weight must be between 1 kg and 300 kg.")
        return weight

    # VALIDATION 5 : Aadhaar: optional but if entered must be exactly 12 digits
    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get('aadhaar_number', '').strip()
        if aadhaar:
            if not aadhaar.isdigit():
                raise forms.ValidationError("Aadhaar number must contain digits only — no letters or special characters.")
            if len(aadhaar) != 12:
                raise forms.ValidationError("Aadhaar number must be exactly 12 digits.")
        return aadhaar

    # VALIDATION 6 : filer_contact: exactly 10 digits, no text, no negatives, no spaces
    def clean_filer_contact(self):
        contact = self.cleaned_data.get('filer_contact', '').strip()
        if not contact:
            raise forms.ValidationError("Contact number is required.")
        if not contact.isdigit():
            raise forms.ValidationError("Contact number must contain digits only — no spaces, letters or special characters.")
        if len(contact) != 10:
            raise forms.ValidationError("Contact number must be exactly 10 digits.")
        return contact


class CaseUpdateForm(forms.ModelForm):

    class Meta:
        model = CaseUpdate
        fields = ['note', 'optional_image']
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Enter any new information, clue, or search progress...'
            }),
            'optional_image': forms.FileInput(attrs={'class': 'form-control'}),
        }