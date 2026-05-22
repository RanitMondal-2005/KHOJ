"""
Django signals that trigger the matching engine automatically when:
  1. A new MissingPerson report is saved (status=ACTIVE)
  2. A new UnidentifiedPatient record is saved (status=UNIDENTIFIED)

Notifications are sent only when new matches are created (not on re-runs).
Uses `created` flag to avoid duplicate notifications on every save.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

# This signal is triggered after a MissingPerson record is saved when status is ACTIVE and its uploaded by the family
@receiver(post_save, sender='family.MissingPerson')
def match_on_missing_person_save(sender, instance, created, **kwargs): # triggered after a MissingPerson record is saved
    """
    Triggered after a MissingPerson record is saved.
    Only runs matching for ACTIVE cases.
    Only notifies on new record creation (not on every field update).
    """
    if instance.status != 'ACTIVE': # only consider active missing persons
        return # else for inactive persons i.e. we don't want to trigger matching

    # Avoid circular imports by importing inside the handler because it prevents import errors like "cannot import name"
    from matching.engine import run_matching_for_missing_person
    from notifications.utils import create_match_notifications
    from matching.models import MatchResult

    # Count existing matches before running engine
    existing_count = MatchResult.objects.filter(missing_person=instance).count()

    # Run matching engine — compares against all UNIDENTIFIED patients
    run_matching_for_missing_person(instance)

    # Count matches after engine run
    new_count = MatchResult.objects.filter(missing_person=instance).count()

    # Only send notification if new matches were actually created
    if new_count > existing_count:
        create_match_notifications(missing_person=instance)

# Basically, this function does the same thing as match_on_missing_person_save but for patients who are unidentified and uploaded by hospitals
@receiver(post_save, sender='hospital.UnidentifiedPatient')
def match_on_patient_save(sender, instance, created, **kwargs): # triggered after an UnidentifiedPatient record is saved
    """
    Triggered after an UnidentifiedPatient record is saved.
    Only runs matching for UNIDENTIFIED patients.
    Only notifies when new matches are created.
    """
    if instance.status != 'UNIDENTIFIED':
        return

    from matching.engine import run_matching_for_patient
    from notifications.utils import create_match_notifications
    from matching.models import MatchResult

    existing_count = MatchResult.objects.filter(unidentified_patient=instance).count() # count matches before engine run so that we can compare later

    run_matching_for_patient(instance) # call matching engine when a new patient is saved in UNIDENTIFIED state in our DB

    new_count = MatchResult.objects.filter(unidentified_patient=instance).count() # count matches after engine run i.e. this count means new matches created

    if new_count > existing_count: # only notify if new matches were created 
        create_match_notifications(unidentified_patient=instance) # send notification to matched users
