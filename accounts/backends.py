"""
accounts/backends.py

WHY THIS FILE EXISTS:
Django's default ModelBackend always queries the database using a 'username' column.
In Khoj, we do not use usernames at all:
1. Family users log in using their Email.
2. Hospital staff can log in using either their Email or their Staff ID.
3. Police officers can log in using either their Email or their Police ID.

HOW DJANGO RUNS THESE:
In settings.py, these three backends are registered in AUTHENTICATION_BACKENDS in sequence:
[EmailBackend, StaffIDBackend, PoliceIDBackend].
When authenticate(request, username=..., password=...) is called:
1. Django passes the credential string to EmailBackend first.
2. If no user matches that email, it returns None, and Django automatically falls through to StaffIDBackend.
3. If no hospital profile matches that staff_id, it returns None, falling through to PoliceIDBackend.
4. If a match is found and the password hashes match, that user is returned and login succeeds.
"""

from django.contrib.auth.backends import ModelBackend # ModelBackend is Django's default backend. By inheriting it we get user_can_authenticate(), authenticate() etc. From here we will just modify the authenticate() method according to our needs & use rest as-is.
from django.contrib.auth import get_user_model # get_user_model is used for retrieving the active user model from the project's settings i.e. AUTH_USER_MODEL

User = get_user_model()   # Find and fetch whichever User model is currently active in this project.
# get_user_model() dynamically reads AUTH_USER_MODEL from settings. So, User simply becomes an alias for KhojUser. Calling User.objects.get(...) runs KhojUser.objects.get(...) safely without triggering import conflicts.


class EmailBackend(ModelBackend):
    """
    Standard email + password login.
    Used by Family users (they only have an email).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # username param here is actually the email typed in the form -> because Django always calls authenticate() with username and password as parameter names — even if the actual field is email.
        if not username or not password: # Check if username or password is not provided
            return None # authentication failed, Try next backend in settings.AUTHENTICATION_BACKENDS.

        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # still run hashing to avoid timing-based username enumeration i.e. password guessing
            User().set_password(password) # User().set_password(password) runs a fake password hash. This is a timing attack prevention trick. 
            # Without it — a hacker could measure response time and determine if the email exists in the database or not. If the email does not exist, it will take less time to respond than if it does exist. By running a fake password hash, we make the response time consistent regardless of whether the email exists or not.
            return None

        # Check if the provided password is correct (check_password hashes the input and compares against stored hash)
        # and user_can_authenticate(user) checks if the user is allowed to authenticate (checks is_active flag)
        if user.check_password(password) and self.user_can_authenticate(user): 
            return user # when both conditions are met, return the user object i.e, user authentication successful

        return None


class StaffIDBackend(ModelBackend):
    """
    Staff ID + password login for Hospital users.
    Triggered when a user types their staff_id into the login identifier field instead of an email.
    Looks up HospitalProfile by staff_id, then retrieves the linked parent KhojUser.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Here 'username' contains whatever string was submitted in the login field (e.g. staff_id)
        if not username or not password:
            return None

        try:
            # Import inside method to avoid circular imports during Django startup
            from accounts.models import HospitalProfile
            # select_related('user') performs a SQL JOIN to pull both HospitalProfile and KhojUser in a single DB query
            profile = HospitalProfile.objects.select_related('user').get(staff_id=username)
            user = profile.user # Get the linked user object from HospitalProfile 
        except Exception:
            # Timing attack prevention: if staff_id is not found, run password hashing calculation anyway so timing matches a valid lookup
            User().set_password(password)
            return None # return None = authentication failed, so Django will try next backend.

        # Verify password against the parent KhojUser's hashed password and check is_active
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None


class PoliceIDBackend(ModelBackend):
    """
    Police ID + password login for Police users.
    Triggered when a user types their police_id into the login identifier field instead of an email.
    Looks up PoliceProfile by police_id, then retrieves the linked parent KhojUser.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Here 'username' contains whatever string was submitted in the login field (e.g. police_id)
        if not username or not password:
            return None

        try: # if already exists, just fetch the user
            # Import inside method to avoid circular imports during Django startup
            from accounts.models import PoliceProfile
            # select_related('user') joins KhojUser and PoliceProfile tables in one SQL statement, avoiding a second query to fetch credentials
            profile = PoliceProfile.objects.select_related('user').get(police_id=username)
            user = profile.user # Get the linked user object
        except Exception:
            # Timing attack prevention: matches execution time of a valid ID check
            User().set_password(password)
            return None # return None = authentication failed. If this is the last backend in the list, authenticate() returns None to the view.

        # Verify password against the parent KhojUser's hashed password and check is_active
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None