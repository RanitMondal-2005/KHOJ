"""
notifications/utils.py

- utils.py is the engine that creates and saves our notifications into the database.
- Only FAMILY and HOSPITAL users receive notifications.
- Called from matching/signals.py after new matches are found for Family OR Hospital.
"""

from django.utils import timezone
from datetime import timedelta
from matching.models import MatchResult
from .models import Notification

def create_match_notifications(missing_person=None, unidentified_patient=None):
    """
    Creates a notification for the relevant party when new matches are found.
    Uses a 1-hour deduplication-preventing duplicate records from being created.
    """
    ONE_HOUR_AGO = timezone.now() - timedelta(hours=1) # (current time - 1 hour) used to filter out duplicate alerts sent within the last 60 minutes
    # timezone.now()-> curr time , timedelta(hours=1) -> simply 1 hr in time

    # ───────────── Notify Family ─────────────
    if missing_person:
        matches = MatchResult.objects.filter( # bring all the PENDING matcheResults for this missing person
            missing_person=missing_person,
            status='PENDING'
        ).order_by('-confidence_score')

        if not matches.exists(): # no pending matches exist (like none cleared the 40% threshold, or all were previously dismissed),immediately exit
            return

        family_user = missing_person.linked_family_user  # Retrieves the specific KhojUser who submitted the report via FK
        top_match = matches.first() # Selects the highest-confidence match candidate
        count = matches.count() # Counts the total number of pending matches waiting for this particular report(For cases like : If the engine finds 4 candidate matches at once(e.g., 85%, 72%, 60%, and 45%)for a particular report, instead of sending 4 separate notifications we create a single aggregated alert informing them:"Potential match found for John Doe. 4 match(es) pending review.")


        # Checks whether a notification has already been sent to this user for this specific match (top_match.id) within the last 60 minutes; if a record exists within that window, recent_exists evaluates to True.
        recent_exists = Notification.objects.filter(
            user=family_user,
            notif_type='MATCH_FOUND',
            related_match_id=top_match.id,
            created_at__gte=ONE_HOUR_AGO,
        ).exists()

        # Executes only when recent_exists is False - meaning this alert is not a duplicate
        if not recent_exists:
            Notification.objects.create( # Create a notification ......
                user=family_user,
                message=(
                    f"Potential match found for {missing_person.person_name}. "
                    f"{count} match(es) pending review."
                ),
                notif_type='MATCH_FOUND', # set Notification Status(notif_type) = MATCH FOUND
                related_match_id=top_match.id, # stores the PK(the ID number) of the highest-scoring candidate match directly inside the notification row to redirect directly to that specific match card through notifications

                # NOTE : The notification only stores the highest-scoring match ID because of how notification works, If the engine finds 4 candidate matches at once (e.g., 85%, 72%, 60%, and 45%), sending 4 separate notifications would flood the user's inbox with redundant noise. Instead,our utility creates a single aggregated alert informing them:"Potential match found for John Doe. 4 match(es) pending review.",Although all matches will be present in the Match Result list, just first highest scored one will be redirected through the link by frontend.
            )

    # ───────────── Notify Hospital ─────────────
    if unidentified_patient:
        matches = MatchResult.objects.filter(
            unidentified_patient=unidentified_patient,
            status='PENDING'
        ).order_by('-confidence_score')

        if not matches.exists():
            return

        hospital_user = unidentified_patient.linked_hospital  # get that Specific KhojUser
        top_match = matches.first()
        count = matches.count()
        name = getattr(unidentified_patient, 'estimated_name', None) or f"Patient #{unidentified_patient.id}"

        recent_exists = Notification.objects.filter(
            user=hospital_user,
            notif_type='PATIENT_IDENTIFIED',
            related_match_id=top_match.id,
            created_at__gte=ONE_HOUR_AGO,
        ).exists()

        if not recent_exists:
            Notification.objects.create(
                user=hospital_user,
                message=(
                    f"Potential match found for {name}. "
                    f"{count} match(es) pending review."
                ),
                notif_type='PATIENT_IDENTIFIED',
                related_match_id=top_match.id,
            )
