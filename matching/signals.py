"""
Django signals that trigger the matching engine automatically when:
  1. A new MissingPerson report is saved (status=ACTIVE)
  2. A new UnidentifiedPatient record is saved (status=UNIDENTIFIED)

"""

from django.db.models.signals import post_save
from django.dispatch import receiver


# ---------------- Triggered after a MissingPerson record is saved ----------------------

@receiver(post_save, sender='family.MissingPerson') # Registers this function as a listener for Django's post_save signal — fires automatically after ANY MissingPerson.save() call anywhere in the code
def match_on_missing_person_save(sender, instance, created, **kwargs):

    # NOTE : instance is the specific database row being created or updated right now & MissingPerson is our Model where it is saved just now.

    if instance.status != 'ACTIVE': # if not ACTIVE cases, no matching runs
        return

    from matching.engine import run_matching_for_missing_person
    from notifications.utils import create_match_notifications
    from matching.models import MatchResult

    # Count existing matches before running engine (It checks the Foreign Key column missing_person_id inside the MatchResult table against the exact database ID (instance.id) of the current record)
    existing_count = MatchResult.objects.filter(missing_person=instance).count()

    # Run matching engine — compares against all UNIDENTIFIED patients
    run_matching_for_missing_person(instance)

    # Count matches after engine run (Same as Prev Line)
    new_count = MatchResult.objects.filter(missing_person=instance).count()

    # Only send notification if new matches were actually created
    if new_count > existing_count:
        # 1. Notify the Family user
        create_match_notifications(missing_person=instance)

        # 2. Notify the Hospital whose patient was matched
        for match in MatchResult.objects.filter(missing_person=instance, status='PENDING'):
            create_match_notifications(unidentified_patient=match.unidentified_patient)



# ---------------- Triggered after a Unidentified Patient record is saved ----------------------

@receiver(post_save, sender='hospital.UnidentifiedPatient')
def match_on_patient_save(sender, instance, created, **kwargs):

    if instance.status != 'UNIDENTIFIED':
        return

    from matching.engine import run_matching_for_patient
    from notifications.utils import create_match_notifications
    from matching.models import MatchResult

    existing_count = MatchResult.objects.filter(unidentified_patient=instance).count()

    run_matching_for_patient(instance)

    new_count = MatchResult.objects.filter(unidentified_patient=instance).count()

    if new_count > existing_count: # only notify if new matches were created
        # 1. Notify the Hospital user
        create_match_notifications(unidentified_patient=instance)

        # 2. Notify the Family whose report was matched
        for match in MatchResult.objects.filter(unidentified_patient=instance, status='PENDING'):
            create_match_notifications(missing_person=match.missing_person)
