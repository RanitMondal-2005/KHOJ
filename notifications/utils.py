"""
notifications/utils.py

Utility functions to create in-app notifications.
Only FAMILY and HOSPITAL users receive notifications.
POLICE receive no notifications (by design).
Called from matching/signals.py after new matches are found.

CORE LOGIC :
USE OF UTILS is that : it provides a centralized way to create notifications without duplicating code across the application. Or else, we would have to write the same notification creation logic in multiple places, increasing the risk of errors and making maintenance more difficult.
This promotes DRY (Don't Repeat Yourself) principles and makes the codebase cleaner and easier to manage.
Its Implementation is straightforward: simply call the appropriate utility function with the necessary parameters, and it handles the rest.

"""

from .models import Notification # Importing the Notification model for creating notifications


def create_match_notifications(missing_person=None, unidentified_patient=None): # Create notifications for new matches
    """
    Creates a notification for the relevant party when new matches are found.

    - missing_person: notify the linked family user
    - unidentified_patient: notify the linked hospital staff user

    Checks for a recent duplicate notification to avoid spamming
    (won't create a second notification if one was sent in the last hour
    for the same case).
    """
    from matching.models import MatchResult 
    from django.utils import timezone
    from datetime import timedelta

    ONE_HOUR_AGO = timezone.now() - timedelta(hours=1) # This is used to filter out recent notifications,and avoid spamming users with duplicate alerts.
    # How its done?-> By checking if a notification of the same type and related match ID exists for the user within the last hour.

    if missing_person:
        # Find pending matches for this case
        matches = MatchResult.objects.filter(
            missing_person=missing_person,
            status='PENDING'
        )
        if not matches.exists(): # If no pending matches exist, return early
            return

        family_user = missing_person.linked_family_user # Get the linked family user 

        # Avoid duplicate notifications within the last hour
        recent_exists = Notification.objects.filter( # its done by checking if a notification of the same type and related match ID exists for the user within the last hour.
            user=family_user, # Get the linked family user
            notif_type='MATCH_FOUND', # Notification type i.e. MATCH_FOUND
            created_at__gte=ONE_HOUR_AGO, # Created at timestamp filter
            related_match_id=matches.first().id, # ID of the related match(most imp) 
        ).exists() 

        if not recent_exists: # If no recent notification exists, create a new one
            Notification.objects.create(
                user=family_user,
                message=( # Message content for the notification
                    f"Potential match found for {missing_person.person_name}. "
                    f"{count} possible match(es) available. Check your matches."
                ),
                notif_type='MATCH_FOUND',
                related_match_id=matches.first().id, # ID of the related match
            )

    # Similar logic for unidentified patients, notifying the linked hospital user
    if unidentified_patient:
        matches = MatchResult.objects.filter(
            unidentified_patient=unidentified_patient,
            status='PENDING'
        )
        if not matches.exists():
            return

        hospital_user = unidentified_patient.linked_hospital
        count = matches.count()
        name = unidentified_patient.estimated_name or f"Patient #{unidentified_patient.id}"

        recent_exists = Notification.objects.filter(
            user=hospital_user,
            notif_type='PATIENT_IDENTIFIED',
            created_at__gte=ONE_HOUR_AGO,
            related_match_id=matches.first().id,
        ).exists()

        if not recent_exists:
            Notification.objects.create(
                user=hospital_user,
                message=(
                    f"Potential match found for {name}. "
                    f"{count} possible match(es) available. Check match alerts."
                ),
                notif_type='PATIENT_IDENTIFIED',
                related_match_id=matches.first().id,
            )
