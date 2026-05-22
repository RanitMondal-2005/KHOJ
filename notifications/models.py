"""
Simple in-app notification model.
Only FAMILY and HOSPITAL users receive notifications.
POLICE do NOT receive notifications.
"""

from django.db import models
from accounts.models import KhojUser # Importing the KhojUser model where we have user information

# Notification model for in-app notifications, This model is needed or else later features like notifications will break 
# for e.g : when we want to create a notification for a user, we need to have a model to store that notification in the database, and also to retrieve it later when we want to display it in the notifications page or in the navbar badge. So this model is essential for the notifications feature to work properly.
class Notification(models.Model):
    """In-app notification for family and hospital users."""

    TYPE_CHOICES = [
        ('MATCH_FOUND', 'Potential Match Found'),
        ('CASE_RESOLVED', 'Case Resolved'),
        ('PATIENT_IDENTIFIED', 'Patient Possibly Identified'),
        ('GENERAL', 'General'),
    ]

    user = models.ForeignKey(KhojUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='GENERAL')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional link to a match (for quick navigation)
    related_match_id = models.PositiveIntegerField(null=True, blank=True) # ID of the related match, if any i.e. basically the match this notification is about..

    class Meta:
        ordering = ['-created_at'] # Arrange by Newest notifications first

    def __str__(self):
        return f"[{self.notif_type}] {self.user.full_name}: {self.message[:50]}" # for admin interface
