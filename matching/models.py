"""
MatchResult stores a potential match between a MissingPerson and UnidentifiedPatient.
score_breakdown stores the per-factor scores as JSON so templates can display
exactly which fields contributed to the match  e.g: {"gender": 20, "age": 10, ...}
JSON is needed as it allows for flexible and dynamic rendering of match details.
With JSON, we can easily add or remove fields from the score breakdown without changing the underlying database schema meaning we can evolve the matching logic over time without disruptive migrations.
Without JSON, adding new fields would require database migrations, potentially causing downtime and requiring careful coordination.
"""

from django.db import models                     # importing Django models
from family.models import MissingPerson         # importing MissingPerson model
from hospital.models import UnidentifiedPatient # importing UnidentifiedPatient model


class MatchResult(models.Model):   # model to store matching results

    STATUS_CHOICES = [   # choices for match verification status
        ('PENDING', 'Pending Review'),   # match is waiting for review
        ('VERIFIED', 'Verified'),        # match confirmed as correct
        ('REJECTED', 'Rejected'),        # match marked incorrect
    ]

    missing_person = models.ForeignKey(
        MissingPerson,                   # links to MissingPerson model
        on_delete=models.CASCADE,       # delete match if missing person is deleted
        related_name='matches'          # allows reverse access using missing_person.matches
    )

    unidentified_patient = models.ForeignKey(
        UnidentifiedPatient,            # links to UnidentifiedPatient model
        on_delete=models.CASCADE,       # delete match if patient is deleted
        related_name='matches'          # allows reverse access using patient.matches
    )

    confidence_score = models.FloatField(
        help_text="Score out of 100"    # helpful admin description
    )

    # stores each factor's score as JSON eg: {"gender": 20, "age": 10, ...}
    # null=True for backward compat with existing rows that don't have it yet and blank=True to allow form submissions without it
    # this is needed to avoid validation errors when creating/updating matches
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

        ordering = ['-confidence_score']
        # highest confidence matches appear first

        unique_together = ('missing_person', 'unidentified_patient')
        # prevents duplicate match entries for same pair

    def __str__(self):   # string representation of object -> for admin interface
        return (
            f"Match: {self.missing_person.person_name} ↔ "   # show missing person's name
            f"Patient #{self.unidentified_patient.id} | "   # show patient ID
            f"Score: {self.confidence_score:.1f}%"          # show confidence score
        )

    @property   # allows method to be accessed like an attribute in templates (basically it creates a template variable) i.e. {{ match.confidence_label }}; meaning it can be used directly in template code.
    def confidence_label(self):

        """Returns (label, bootstrap_color) tuple for template use."""

        score = self.confidence_score   # store confidence score in variable

        if score >= 80:
            return ('HIGH', 'success')
            # very strong match → green bootstrap badge

        elif score >= 60:
            return ('MODERATE', 'warning')
            # medium confidence match → yellow bootstrap badge

        else:
            return ('LOW', 'secondary')
            # weak confidence match → gray bootstrap badge