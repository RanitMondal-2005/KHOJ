"""
family/forms.py

MissingPersonForm - updated with new fields (aadhaar, relation, filer details)
and proper validation for age (1-100), height, weight (positive integers only).
"""

from django import forms
from .models import MissingPerson, CaseUpdate


class MissingPersonForm(forms.ModelForm):

    class Meta:
        model = MissingPerson
        exclude = ['linked_family_user', 'status', 'created_at', 'updated_at', 'contact_number']
        widgets = {
            'person_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '1', 'max': '100', 'step': '1'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'cm', 'min': '1', 'step': '1'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'kg', 'min': '1', 'step': '1'
            }),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'eye_color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Brown'}),
            'hair_color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Black'}),
            'skin_tone': forms.Select(attrs={'class': 'form-select'}),
            'identifying_marks': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Scars, tattoos, birthmarks...'
            }),
            'clothing_description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Last known clothing...'
            }),
            'aadhaar_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '12-digit Aadhaar number', 'maxlength': '12'
            }),
            'relation': forms.Select(attrs={'class': 'form-select'}),
            'filer_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your contact number'}),
            'filer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email (optional)'}),
            'last_seen_location': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'last_seen_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fir_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'police_station_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
        }

    # age: must be between 1 and 100, no decimals
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None:
            raise forms.ValidationError("Age is required.")
        if age < 1 or age > 100:
            raise forms.ValidationError("Age must be between 1 and 100.")
        return age

    # height: must be positive, no decimals (PositiveIntegerField handles no negative)
    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height is None:
            raise forms.ValidationError("Height is required.")
        if height < 1:
            raise forms.ValidationError("Height must be a positive number.")
        if height > 300:
            raise forms.ValidationError("Please enter a valid height in cm.")
        return height

    # weight: must be positive, no decimals
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is None:
            raise forms.ValidationError("Weight is required.")
        if weight < 1:
            raise forms.ValidationError("Weight must be a positive number.")
        if weight > 500:
            raise forms.ValidationError("Please enter a valid weight in kg.")
        return weight

    # Aadhaar: optional but if entered must be exactly 12 digits
    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get('aadhaar_number', '').strip()
        if aadhaar and (not aadhaar.isdigit() or len(aadhaar) != 12):
            raise forms.ValidationError("Aadhaar number must be exactly 12 digits.")
        return aadhaar


class CaseUpdateForm(forms.ModelForm):

    class Meta:
        model = CaseUpdate
        fields = ['note', 'optional_image']
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Enter any new information, clue, or search progress...'
            }),
            'optional_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }