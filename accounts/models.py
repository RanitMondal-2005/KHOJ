"""
accounts/models.py

WHY THIS FILE EXISTS:
By default, Django's built-in User system forces everyone to log in with a 'username' and 'password'.
In Khoj, we don't want usernames. We need:
1. Family users to log in using their Email.
2. Hospital staff and Police officers to log in using their unique Institutional IDs (staff_id / police_id) or Email.
3. Extra details for institutions (like hospital address or police station name) that standard Django users don't have.

HOW WE SOLVE IT:
- KhojUserManager: Custom manager that creates users, lowercases emails, and safely hashes passwords.
- KhojUser: REPLACES DJANGO'S DEFAULT USER MODEL ENTIRELY. Sets 'email' as the main login field (USERNAME_FIELD).
- HospitalProfile & PoliceProfile: Separate tables linked 1-to-1 with KhojUser to store institutional details and IDs without cluttering the main user table.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Custom manager for KhojUser -> This manager knows how to create KhojUser objects correctly.
class KhojUserManager(BaseUserManager):
    def create_user(self, email, full_name, role, password=None, **extra_fields):
        """
        Creates and saves a regular KhojUser with normalized email, role, and hashed password.
        Called by registration forms and user creation services. 
        NOTE: We don't instantiate KhojUser directly. We call KhojUser.objects.create_user(),
        which routes through this manager to hash passwords and validate fields before finally saving to the DB.
        """
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email) # lowercase the domain part of the email
        user = self.model(email=email, full_name=full_name, role=role, **extra_fields) # create user instance with help of KhojUser
        # self.model -> points to whichever model the manager is attached to . For now it refers to KhojUser. We used to self.model instead of hardcoding, user = KhojUser(email=email,full_name=full_name,...)
        user.set_password(password) # Hashes the plain-text password using PBKDF2/Argon2 before saving
        user.save(using=self._db) # saving user to DB , and user=self._db is means -> use whichever database is currently configured.
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields): # called when creating a superuser for Django admin
        """
        Creates a superuser (manage.py createsuperuser) for Django Admin Panel.
        Does 3 things - 
        """
        extra_fields.setdefault('is_staff', True) # Grants access to log into Django Admin (/admin/)
        extra_fields.setdefault('is_superuser', True) # Grants master permissions across all tables and models in admin panel
        return self.create_user(email, full_name, role='FAMILY', password=password, **extra_fields) # Give admin a role as Family, ### NOTE : ANY USER WITH JUST ROLE==FAMILY CANT JUST LOGIN IN ADMIN AS ABOVE 2 FIELD WILL RESTRICT THEM .

# Custom user model for Khoj -> THE BLUEPRINT FOR DATABASE USER TABLE to define which fields will be present for user.
class KhojUser(AbstractBaseUser, PermissionsMixin):
    """
    Base user model for Khoj.
    All three role types (Family, Hospital, Police) use this model.
    Hospital and Police have additional profile models for institutional fields.
    
    Inheritance:
    - AbstractBaseUser: Handles password hashing, last_login tracking, and core auth methods.
    - PermissionsMixin: Handles groups, user_permissions, is_superuser flag, and permission caching.
    """

    ROLE_CHOICES = [
        ('FAMILY', 'Family'),
        ('HOSPITAL', 'Hospital Staff'),
        ('POLICE', 'Police Officer'),
    ]

    # Core identification & role attributes
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True) # Serves as the primary unique credential instead of a traditional username
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Django administrative & status flags
    is_active = models.BooleanField(default=True) # Deactivating accounts sets this to False rather than deleting rows
    is_staff = models.BooleanField(default=False) # Determines access to the Django Admin (/admin/) panel ; by default False for all users unless typed create superuser
    date_joined = models.DateTimeField(auto_now_add=True)

    # Override PermissionsMixin M2M fields to set unique related_names
    # To avoid Clash with Django's default User and our KhojUser in the same project.
    groups = models.ManyToManyField(
        'auth.Group', 
        blank=True,
        related_name='khojuser_set', # custom name to avoid clash with default User model
        related_query_name='khojuser', 
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='khojuser_set',
        related_query_name='khojuser',
        verbose_name='user permissions',
    )

    # Configuration for Django Auth Framework:
    # 1. USERNAME_FIELD dictates what field is treated as the primary identifier during authentication
    # 2. REQUIRED_FIELDS defines the prompts presented during manage.py createsuperuser (excluding USERNAME_FIELD & password)
    USERNAME_FIELD = 'email' # making email act as the username throughout Django's auth system
    REQUIRED_FIELDS = ['full_name']

    objects = KhojUserManager() # connecting KhojUserManager to KhojUser i.e, internally it is KhojUserManager.model = KhojUser 

    def __str__(self):
        # Human-readable string representation used in Django Admin lists and shell debugging
        return f"{self.full_name} ({self.role})"

    # Role check helper properties:
    # Allows template tags and view logic to inspect authorization cleanly:
    # e.g., {% if request.user.is_family %} or `if user.is_hospital:`
    @property
    def is_family(self):
        return self.role == 'FAMILY'

    @property
    def is_hospital(self):
        return self.role == 'HOSPITAL'

    @property
    def is_police(self):
        return self.role == 'POLICE'
    
    # @property makes these callable like attributes, not methods — so we can use user.is_family instead of writting user.is_family()



# ----------- EXTENDED PROFILE MODELS FOR HOSPITAL AND POLICE USERS -----------

class HospitalProfile(models.Model):
    """
    Extended profile for Hospital Staff users.
    Stores institutional details for the hospital.
    staff_id acts as their institutional identifier - login via staffID is handled in backends.py 
    Linked 1-to-1 with KhojUser: accessed via `user.hospital_profile`.
    """

    user = models.OneToOneField(KhojUser, on_delete=models.CASCADE, related_name='hospital_profile')
    staff_id = models.CharField(max_length=50, unique=True) # Used for institutional login via StaffIDBackend
    hospital_registration_id = models.CharField(max_length=100)  # Stored for future verification
    hospital_name = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=10) # 10-digit primary emergency contact number
    hospital_email = models.EmailField() # Official institutional contact email

    def __str__(self):
        return f"{self.hospital_name} - {self.staff_id}"


class PoliceProfile(models.Model):
    """
    Extended profile for Police users.
    Stores institutional details for the police station.
    police_id acts as their institutional identifier - login via policeID is handled in backends.py
    Linked 1-to-1 with KhojUser: accessed via `user.police_profile`.
    """

    user = models.OneToOneField(KhojUser, on_delete=models.CASCADE, related_name='police_profile')
    police_id = models.CharField(max_length=50, unique=True) # Used for institutional login via PoliceIDBackend
    police_station_registration_id = models.CharField(max_length=100)  # Stored for future verification
    police_station_name = models.CharField(max_length=200)
    district = models.CharField(max_length=100) # Used to filter/investigate regional cases within jurisdiction

    def __str__(self):
        return f"{self.police_station_name} - {self.police_id}"