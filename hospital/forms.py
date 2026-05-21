from django import forms
from .models import UnidentifiedPatient


class UnidentifiedPatientForm(forms.ModelForm):

    class Meta:
        model = UnidentifiedPatient
        exclude = ['linked_hospital', 'status', 'created_at', 'updated_at']
        widgets = {
            'estimated_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Leave blank if completely unknown'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'Estimated age',
                'min': '1', 'max': '120', 'step': '1'
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
            'identifying_marks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'clothing_description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'e.g. Blue shirt, black trousers, brown sandals...'
            }),
            'found_id_type': forms.Select(attrs={'class': 'form-select'}),
            'found_id_last4': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Last 4 digits only',
                'maxlength': '4', 'pattern': '[0-9]{4}'
            }),
            'found_location': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'condition_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height is None or height < 1:
            raise forms.ValidationError("Height must be a positive number.")
        if height > 300:
            raise forms.ValidationError("Please enter a valid height in cm.")
        return height

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is None or weight < 1:
            raise forms.ValidationError("Weight must be a positive number.")
        if weight > 500:
            raise forms.ValidationError("Please enter a valid weight in kg.")
        return weight

    def clean_found_id_last4(self):
        last4 = self.cleaned_data.get('found_id_last4', '').strip()
        id_type = self.cleaned_data.get('found_id_type', '')
        # if an ID type was selected, last4 becomes required
        if id_type and not last4:
            raise forms.ValidationError("Please enter the last 4 digits of the ID.")
        if last4 and (not last4.isdigit() or len(last4) != 4):
            raise forms.ValidationError("Must be exactly 4 digits.")
        return last4