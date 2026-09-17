"""
matching/models.py

MatchResult DB Table stores a potential match between a MissingPerson and UnidentifiedPatient.
- score_breakdown stored as JSON so templates can display
  exactly which fields contributed to the match  e.g: {"face_match": 22, "age": 10, ...}

- JSON is needed as it allows for flexible and dynamic rendering of match details.

"""

from django.db import models
from family.models import MissingPerson
from hospital.models import UnidentifiedPatient

# ----------------- model to store matching results -----------------

class MatchResult(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'), # Default on creation
        ('VERIFIED', 'Verified'), # Currently unused — future scope
        ('REJECTED', 'Rejected'), # Dismiss a particular match
    ]

    # MatchResult has 2 FK -> one of MissingPerson & one of Unidentified Patient Model
    missing_person = models.ForeignKey(
        MissingPerson,
        on_delete=models.CASCADE,
        related_name='matches'          # allows FK reverse lookup using missing_person.matches
    )

    unidentified_patient = models.ForeignKey(
        UnidentifiedPatient,
        on_delete=models.CASCADE,
        related_name='matches'          # allows FK reverse lookup using patient.matches
    )

    confidence_score = models.FloatField(
        help_text="Score out of 100"    # helpful admin description
    )

    # Score Breakdown field -> a JSON field
    score_breakdown = models.JSONField(
        null=True,                      # database can store NULL values; because we want to allow existing rows without this field
        blank=True                      # form field can be left empty; as it is not required for match creation
    )

    status = models.CharField(
        max_length=10,                  # maximum length of status text
        choices=STATUS_CHOICES,         # only allowed values from STATUS_CHOICES
        default='PENDING'               # default status when object created
    )

    created_at = models.DateTimeField(
        auto_now_add=True               # automatically stores creation timestamp
    )

    class Meta:   # extra model configurations
        ordering = ['-confidence_score'] # highest confidence matches appear first
        unique_together = ('missing_person', 'unidentified_patient') # prevents duplicate match entries for same pair


    def __str__(self):   # string representation of object -> for admin interface
        return (
            f"Match: {self.missing_person.person_name} ↔ "   # show missing person's name
            f"Patient #{self.unidentified_patient.id} | "   # show patient ID
            f"Score: {self.confidence_score:.1f}%"          # show confidence score
        )

    @property
    def confidence_label(self):
        """Returns (label, bootstrap_color) tuple for template use."""
        score = self.confidence_score   # store confidence score in variable

        if score >= 80:
            return ('HIGH', 'success') #  green bootstrap badge

        elif score >= 60:
            return ('MODERATE', 'warning') # yellow bootstrap badge

        else:
            return ('LOW', 'secondary') # gray bootstrap badge
