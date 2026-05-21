from django.db import models
from accounts.models import KhojUser


class UnidentifiedPatient(models.Model):

    GENDER_CHOICES = [
        ('MALE', 'Male'), ('FEMALE', 'Female'),
        ('OTHER', 'Other'), ('UNKNOWN', 'Unknown'),
    ]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
        ('UNKNOWN', 'Unknown'),
    ]
    SKIN_TONE_CHOICES = [
        ('FAIR', 'Fair'), ('WHEATISH', 'Wheatish'),
        ('MEDIUM', 'Medium'), ('DARK', 'Dark'), ('UNKNOWN', 'Unknown'),
    ]
    STATUS_CHOICES = [
        ('UNIDENTIFIED', 'Unidentified'),
        ('IDENTIFIED', 'Identified'),
    ]
    # types of ID that might be found on the person
    ID_TYPE_CHOICES = [
        ('', 'No ID Found'),
        ('AADHAAR', 'Aadhaar Card'),
        ('PAN', 'PAN Card'),
        ('VOTER', 'Voter ID'),
        ('DRIVING', 'Driving Licence'),
        ('PASSPORT', 'Passport'),
        ('OTHER', 'Other ID'),
    ]

    linked_hospital = models.ForeignKey(
        KhojUser, on_delete=models.CASCADE, related_name='patient_records'
    )

    estimated_name = models.CharField(max_length=150, blank=True)
    age = models.PositiveIntegerField(help_text="Estimated age")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='UNKNOWN')
    height = models.PositiveIntegerField(help_text="Estimated height in cm")
    weight = models.PositiveIntegerField(help_text="Estimated weight in kg")
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='UNKNOWN')
    eye_color = models.CharField(max_length=50, blank=True)
    hair_color = models.CharField(max_length=50, blank=True)
    skin_tone = models.CharField(max_length=20, choices=SKIN_TONE_CHOICES, default='UNKNOWN')
    identifying_marks = models.TextField(blank=True)

    # what the patient was wearing when found - required, helps match with family report
    clothing_description = models.TextField(
        help_text="Clothing worn when found - helps with matching"
    )

    # ID found on the person - only last 4 digits stored for privacy
    found_id_type = models.CharField(
        max_length=20, choices=ID_TYPE_CHOICES, blank=True, default='',
        help_text="Type of ID found on the person (if any)"
    )
    found_id_last4 = models.CharField(
        max_length=4, blank=True,
        help_text="Last 4 digits of the ID number only"
    )

    found_location = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    condition_notes = models.TextField(blank=True)

    # 3 photos required
    face_image = models.ImageField(upload_to='patients/face/')
    full_body_image = models.ImageField(upload_to='patients/fullbody/')
    side_profile_image = models.ImageField(upload_to='patients/side/')

    admission_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='UNIDENTIFIED')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = self.estimated_name or "Unknown"
        return f"Patient: {name} | {self.district} | {self.status}"

    class Meta:
        ordering = ['-created_at']