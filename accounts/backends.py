"""
Custom auth backend so users log in with email instead of username.
Django's default backend looks for 'username' field - we don't have that.We need to tell Django "here's how to find a user instead of looking for a username field".

For Police and Hospital users the login page accepts their institutional ID
in the username field and we do a two-step lookup: first try email, then
try staff_id / police_id if the email lookup fails.
This way all three role types can log in from their respective login pages.
"""

from django.contrib.auth.backends import ModelBackend # ModelBackend is Django's default backend. By inheriting it we get user_can_authenticate(),authenticate() etc. From here we will just modify the authenticate() method according to our needs & use rest as-is.
from django.contrib.auth import get_user_model # get_user_model is used for retrieving the active user model from the project's settings i.e. AUTH_USER_MODEL

User = get_user_model()  # get_user_model() reads AUTH_USER_MODEL from settings. If someone ever changes the user model, this file adapts automatically. So, we use it instead of directly importing the User model i.e, from accounts.models import KhojUser.


class EmailBackend(ModelBackend):
    """
    Standard email + password login.
    Used by Family users (they only have an email).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # username param here is actually the email typed in the form -> because Django always calls authenticate() with username and password as parameter names — even if the actual field is email.
        if not username or not password: # Check if username or password is not provided
            return None # authentication failed, Try next.

        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # still run hashing to avoid timing-based username enumeration i.e. password guessing
            User().set_password(password) # # User().set_password(password) runs a fake password hash. This is a timing attack prevention trick. 
            # Without it — a hacker could measure response time and determine if the email exists in the database or not. If the email does not exist, it will take less time to respond than if it does exist. By running a fake password hash, we make the response time consistent regardless of whether the email exists or not.
            return None

        if user.check_password(password) and self.user_can_authenticate(user): # Check if the provided password is correct, check_password — hashes the input and compares against stored hash and user_can_authenticate(user) checks if the user is allowed to authenticate (checks is_active flag)
            return user # when both conditions are met, return the user object i.e, user authentication successful

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
            user = profile.user # Get the linked user object from HospitalProfile 
        except Exception:
            User().set_password(password) # This is a timing attack prevention trick.
            return None # # return None = authentication failed, so Django will try next backend.

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
        except Exception:
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None