"""
family/forms.py

MissingPersonForm - For Family Members
"""

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
                'minlength': '2',
                'maxlength': '50',
                'pattern': r"[A-Za-z\s.'-]+",
                'title': 'Name should only contain letters, spaces, hyphens, apostrophes, or periods.', # Browser will display this message when any check fails
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '1', 'max': '100', 'step': '1' # restrict age to 1-100 (with no decimals or negatives) but this is only for browser side validation which can be bypassed, so we used this same in clean_age()
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'cm', 'min': '1', 'step': '1'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'kg', 'min': '1', 'step': '1'
            }),
            'blood_group': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),

            'eye_color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Brown',
                'minlength': '3',
                'maxlength': '15',
                'pattern': r'[A-Za-z\s-]+',
                'title': 'Eye color should only contain letters, spaces, or hyphens (e.g., Hazel, Dark-Brown).',
            }),

            'hair_color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Black',
                'minlength': '3',
                'maxlength': '15',
                'pattern': r'[A-Za-z\s-]+',
                'title': 'Hair color should only contain letters, spaces, or hyphens (e.g., Dark Brown, Red-Orange).',
            }),
            'skin_tone': forms.Select(attrs={'class': 'form-select'}),
            'identifying_marks': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Scars, tattoos, birthmarks...', 'max-length':'500' # rows: 3 controls the height of the textarea — it tells the browser to render the textarea tall enough to show 3 lines of text at once initially.
            }),
            'clothing_description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Last known clothing...' , 'max-length':'700'
            }),
            'aadhaar_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '12-digit Aadhaar number', 'maxlength': '12' , 'pattern': '[0-9]{10}'
            }),
            'relation': forms.Select(attrs={'class': 'form-select'}),
            'filer_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your 10-digit contact number',
                'maxlength': '10',        # browser won't let to type more than 10 Characters
                'pattern': '[0-9]{10}',   # browser hints digits only
            }),
            'filer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email (optional)'}),
            'last_seen_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Near City Metro Station, Gate No. 2',
                'minlength': '3',
                'maxlength': '150',
                'pattern': r"^[A-Za-z0-9\s.,#'\-/]+$",
                'title': 'Location can include letters, numbers, spaces, and punctuation like commas, periods, hashes, hyphens, and slashes.',
            }),

            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. North 24 Parganas',
                'minlength': '2',
                'maxlength': '50',
                'pattern': r"^[A-Za-z0-9\s.'-]+$",
                'title': 'District name should only contain letters, numbers, spaces, periods, apostrophes, or hyphens.',
            }),
            'last_seen_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fir_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional (e.g., 124/2026)',
                'maxlength': '30',
                'pattern': r'^[A-Za-z0-9/\s-]*$', # "*" instead of "+" in the regex - ensures that if the user leaves the field completely blank, the browser still allows the form to submit without throwing an error.
                'title': 'Can only contain letters, numbers, slashes (/), spaces, and hyphens (-).',
            }),
            'police_station_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional (e.g., Central Police Station)',
                'maxlength': '100',
                'pattern': r'^[A-Za-z0-9\s.,\'-]*$',
                'title': 'Can only contain letters, numbers, spaces, periods, apostrophes, commas, and hyphens.',
            }),
        }

    # ------- Server Side Validation for restricting age, height, weight & Aadhaar & Contact No ---------

    # VALIDATION 1 : age: must be between 1 and 100, no decimals and no negatives
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None:
            raise forms.ValidationError("Age is required.")
        if age < 1 or age > 100:
            raise forms.ValidationError("Age must be between 1 and 100.")
        return age

    # VALIDATION 2 : height: must be positive, no decimals (PositiveIntegerField handles no negative)
    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height is None:
            raise forms.ValidationError("Height is required.")
        if height < 1:
            raise forms.ValidationError("Height must be a positive number.")
        if height > 300:
            raise forms.ValidationError("Please enter a valid height in cm.")
        return height

    # VALIDATION 3 : weight: must be positive, no decimals
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is None:
            raise forms.ValidationError("Weight is required.")
        if weight < 1:
            raise forms.ValidationError("Weight must be a positive number.")
        if weight > 500:
            raise forms.ValidationError("Please enter a valid weight in kg.")
        return weight

    # VALIDATION 4 : Aadhaar: optional but if entered must be exactly 12 digits
    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get('aadhaar_number', '').strip()
        if aadhaar:
            if not aadhaar.isdigit():
                raise forms.ValidationError("Aadhaar number must contain digits only — no letters or special characters.")
            if len(aadhaar) != 12:
                raise forms.ValidationError("Aadhaar number must be exactly 12 digits.")
        return aadhaar

    # VALIDATION 5 : filer_contact: exactly 10 digits, no text, no negatives, no spaces
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