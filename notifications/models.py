"""
Simple in-app notification model.
- Both FAMILY and HOSPITAL users receive notifications upon valid match.
"""

from django.db import models
from accounts.models import KhojUser

# --------------- Notification model (DB Table) for in-app notifications ---------------

class Notification(models.Model):

    TYPE_CHOICES = [
        ('MATCH_FOUND', 'Potential Match Found'), # Sent to family when their report gets a new match
        ('CASE_RESOLVED', 'Case Resolved'),  # Currently unused
        ('PATIENT_IDENTIFIED', 'Patient Possibly Identified'), # Sent to hospital when their patient gets a new match
        ('GENERAL', 'General'), # Currently unused
    ]

    user = models.ForeignKey(KhojUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='GENERAL') # In utils.py, code explicitly passes the exact notif_type(== MATCH_FOUND/IDENTIFIED) every single time Notification.objects.create(...) is executed, so the default value is simply bypassed.
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Link to a specific match (for quick navigation)
    related_match_id = models.PositiveIntegerField(null=True, blank=True) # stores the PK(id)of the corresponding MatchResult record as a plain integer.It holds the exact numeric ID needed to construct template anchors (such as href="{% url 'family:dashboard' %}#match-{{ notif.related_match_id }}") so users are scrolled directly to the relevant card.
    # NOTE : We didnt Used a FK here - So that The notification remains atleast in the user's historical feed even after the underlying match candidate no longer exists in the active queue.


    class Meta:
        ordering = ['-created_at'] # Arrange by Newest notifications first

    def __str__(self):
        return f"[{self.notif_type}] {self.user.full_name}: {self.message[:50]}" # for admin interface
