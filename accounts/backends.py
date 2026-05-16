"""
Custom auth backend so users log in with email instead of username.
Django's default backend looks for 'username' field - we don't have that.

For Police and Hospital users the login page accepts their institutional ID
in the username field and we do a two-step lookup: first try email, then
try staff_id / police_id if the email lookup fails.
This way all three role types can log in from their respective login pages.
"""

from django.contrib.auth.backends import ModelBackend # ModelBackend is used to customize authentication backends by allowing different fields for user identification
from django.contrib.auth import get_user_model # get_user_model is used for retrieving the active user model from the project's settings i.e. AUTH_USER_MODEL

User = get_user_model()  


class EmailBackend(ModelBackend):
    """
    Standard email + password login.
    Used by Family users (they only have an email).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # username param here is actually the email typed in the form
        if not username or not password: # Check if username or password is not provided
            return None

        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # still run hashing to avoid timing-based username enumeration i.e. password guessing
            User().set_password(password) # store hashed password
            return None

        if user.check_password(password) and self.user_can_authenticate(user): # Check if the provided password is correct and if the user is allowed to authenticate (not inactive)
            return user

        return None


class StaffIDBackend(ModelBackend):
    """
    Staff ID + password login for Hospital users.
    Looks up HospitalProfile by staff_id, then gets the linked user.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try:
            from accounts.models import HospitalProfile
            profile = HospitalProfile.objects.select_related('user').get(staff_id=username)
            user = profile.user
        except Exception:
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None


class PoliceIDBackend(ModelBackend):
    """
    Police ID + password login for Police users.
    Looks up PoliceProfile by police_id, then gets the linked user.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try: # if already exists, just fetch the user
            from accounts.models import PoliceProfile
            profile = PoliceProfile.objects.select_related('user').get(police_id=username) # select_related is used to optimize database queries by fetching related user object in the same query, reducing the number of database hits
            user = profile.user # Get the linked user object
        except Exception: # If the profile does not exist, create a new user
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None