"""
accounts/models.py

WHY THIS FILE EXISTS:
By default, Django's built-in User system forces everyone to log in with a 'username' and 'password'.
In Khoj, we don't want usernames. We need:
1. Family users to log in using their Email.
2. Hospital staff to log in using their unique Institutional IDs (staff_id).
3. Extra details for institutions (like hospital address) that standard Django users don't have.

HOW WE SOLVE IT & CORE CONCEPTS:
- KhojUser:
    * THIS IS THE ONLY USER TABLE IN THE DATABASE. Creates a database table because it inherits from AbstractBaseUser (which inherits from models.Model).
     NOTE : Only classes inheriting from models.Model create database tables in Django. If any class not inheriting this models.Model, it will never be created as a DB Table by Django.
    * Replaces Django's default User model entirely. Django recognizes KhojUser as the project's official user model because of this line : AUTH_USER_MODEL = 'accounts.KhojUser' in settings.py.
    * Sets 'email' as the unique login field (USERNAME_FIELD).
- KhojUserManager:
    * NOT A DATABASE TABLE. It is a Python helper class.
    * Handles pre-save chores: lowercases emails, validates required data, and hashes passwords.
    * You never call `KhojUser(...)` or `KhojUserManager(...)` directly to create users.
    - How the call works in code:
        * Code calls: `KhojUser.objects.create_user(...)`
        * 1st: `KhojUserManager.create_user()` is triggered to clean the email and hash the password.
        * 2nd: The manager uses `self.model(...)` to build and save the `KhojUser` database row.
- HospitalProfile:
    * Separate database table linked 1-to-1 with KhojUser for hospital-specific data.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# Custom manager for KhojUser -> Pure Python helper class (NO database table is created for this).
class KhojUserManager(BaseUserManager):
    """
    Manager helper for KhojUser.
    When you call KhojUser.objects.create_user(...), it runs this class FIRST.
    """
    def create_user(self, email, full_name, role, password=None, **extra_fields):
        """
        Creates and saves a new User with normalized email, role, and hashed password in KhojUser DB Table.
        """
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)  # Lowercases domain part: User@HOSPITAL.ORG -> User@hospital.org
        user = self.model(email=email, full_name=full_name, role=role, **extra_fields)  # Builds KhojUser in memory(Just initialized, DB is not touched yet); self.model -> means use the model class that this manager is attached to. Here,self.model points back to KhojUser Class.
        # user = self.model(...) line ta execute kora mane directly KhojUser(...) Class(model) ke call kora. Django-r built-in models.Model (that KhojUser Class inherits from AbstractBaseuser) logic er jonno email, full_name, role shob field gulo memory te (RAM e) initialize hoye jay. Ekhono kintu Database touch-o hoyni!
        user.set_password(password)          # Hashes plain password string into hashed password
        user.save(using=self._db)            # Now The user is finally SAVED to DB
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """
        Creates an admin user (python manage.py createsuperuser).
        Does 3 things -
        """
        extra_fields.setdefault('is_staff', True) # Grants access to log into Django Admin (/admin/)
        extra_fields.setdefault('is_superuser', True) # Grants master permissions across all tables and models in admin panel
        return self.create_user(email, full_name, role='FAMILY', password=password, **extra_fields) # Re-uses create_user method above to handle its job with giving Admin a default ROLE == FAMILY


# Custom user model for Khoj -> THE DATABASE TABLE BLUEPRINT.
# Only this class creates the database table (accounts_khojuser).
class KhojUser(AbstractBaseUser, PermissionsMixin):
    """
    Base user database table for all Khoj accounts.
    STORES identity credentials (email, password, role) for all users.
    """

    ROLE_CHOICES = [
        ('FAMILY', 'Family'),
        ('HOSPITAL', 'Hospital Staff'),
        ('POLICE', 'Police Officer'),
    ]

    # Core identification & role attributes
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)  # Acts as the login identifier instead of username
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Django administrative & status flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Custom related_names to avoid naming collisions with Django's default auth tables
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='khojuser_set',
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

    # Django Authentication Configuration:
    # 1. USERNAME_FIELD: Treat 'email' as the login username across Django's auth system.
    # 2. REQUIRED_FIELDS: Extra fields prompted when running createsuperuser via terminal.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    # Attaches KhojUserManager as the model's database gateway.
    # This enables the syntax: KhojUser.objects.create_user(...)
    objects = KhojUserManager()

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    # Clean shortcut properties for templates and views (e.g., if user.is_hospital:)
    @property
    def is_family(self):
        return self.role == 'FAMILY'

    @property
    def is_hospital(self):
        return self.role == 'HOSPITAL'

    # @property makes these callable like attributes, not methods — so we can use user.is_family instead of writting user.is_family()


# ----------- EXTENDED PROFILE MODELS FOR HOSPITAL AND POLICE USERS -----------

class HospitalProfile(models.Model):
    """
    Extended profile for Hospital Staff users.
    Stores hospital details and staff identifiers.
    Linked 1-to-1 with KhojUser: accessed via `user.hospital_profile`.
    """

    user = models.OneToOneField(KhojUser, on_delete=models.CASCADE, related_name='hospital_profile')
    staff_id = models.CharField(max_length=50, unique=True)  # Used for institutional login via StaffIDBackend
    hospital_registration_id = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=10)
    hospital_email = models.EmailField()

    def __str__(self):
        return f"{self.hospital_name} - {self.staff_id}"


# POLICE IS NOW REMOVED - But Retained in models to avoid schema migration rollbacks.
class PoliceProfile(models.Model):
    """
    Extended profile for Police users.
    Linked 1-to-1 with KhojUser: accessed via `user.police_profile`.
    """

    user = models.OneToOneField(KhojUser, on_delete=models.CASCADE, related_name='police_profile')
    police_id = models.CharField(max_length=50, unique=True)
    police_station_registration_id = models.CharField(max_length=100)
    police_station_name = models.CharField(max_length=200)
    district = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.police_station_name} - {self.police_id}"
