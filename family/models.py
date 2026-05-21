"""
family/models.py

MissingPerson - the main report filed by a family user.
CaseUpdate    - private notes/clues added by the family to their own case.

New fields added:
  - aadhaar_number  (Aadhaar of the missing person)
  - relation        (filer's relation to the missing person)
  - filer_contact   (contact number of the person filing the report)
  - filer_email     (email of the person filing the report)
"""

from django.db import models
from accounts.models import KhojUser


class MissingPerson(models.Model):

    GENDER_CHOICES = [
        ('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other'),
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
        ('ACTIVE', 'Active'), ('FOUND', 'Found'), ('CLOSED', 'Closed'),
    ]
    RELATION_CHOICES = [
        ('FATHER', 'Father'), ('MOTHER', 'Mother'),
        ('BROTHER', 'Brother'), ('SISTER', 'Sister'),
        ('SPOUSE', 'Spouse'), ('SON', 'Son'), ('DAUGHTER', 'Daughter'),
        ('RELATIVE', 'Other Relative'), ('FRIEND', 'Friend'),
        ('GUARDIAN', 'Guardian'), ('OTHER', 'Other'),
    ]

    linked_family_user = models.ForeignKey(
        KhojUser, on_delete=models.CASCADE, related_name='missing_reports'
    )

    # ── person details ──────────────────────────────────────────
    person_name = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    height = models.PositiveIntegerField(help_text="Height in cm")
    weight = models.PositiveIntegerField(help_text="Weight in kg")
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='UNKNOWN')
    eye_color = models.CharField(max_length=50)
    hair_color = models.CharField(max_length=50)
    skin_tone = models.CharField(max_length=20, choices=SKIN_TONE_CHOICES, default='UNKNOWN')
    identifying_marks = models.TextField(blank=True)
    clothing_description = models.TextField(blank=True)

    # Aadhaar of the missing person - stored but not verified
    aadhaar_number = models.CharField(
        max_length=12, blank=True,
        help_text="12-digit Aadhaar number of the missing person (if known)"
    )

    # ── filer details (person filling the form) ─────────────────
    relation = models.CharField(
        max_length=20, choices=RELATION_CHOICES,
        help_text="Your relation to the missing person"
    )
    filer_contact = models.CharField(
        max_length=15,
        help_text="Your contact number"
    )
    filer_email = models.EmailField(
        blank=True,
        help_text="Your email address (optional, for coordination)"
    )

    # ── location ────────────────────────────────────────────────
    last_seen_location = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    last_seen_date = models.DateField()

    # photos - both required
    passport_photo = models.ImageField(upload_to='missing/passport/')
    full_body_photo = models.ImageField(upload_to='missing/fullbody/')

    # kept for compatibility - old contact_number field
    contact_number = models.CharField(max_length=15, blank=True)

    # police info - optional
    fir_number = models.CharField(max_length=100, blank=True)
    police_station_name = models.CharField(max_length=200, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person_name} - {self.district} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class CaseUpdate(models.Model):
    """Private notes/clues added by the family. Not public sightings."""

    linked_missing_person = models.ForeignKey(
        MissingPerson, on_delete=models.CASCADE, related_name='case_updates'
    )
    note = models.TextField()
    optional_image = models.ImageField(upload_to='updates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update for {self.linked_missing_person.person_name} at {self.created_at:%d %b %Y}"

    class Meta:
        ordering = ['-created_at']