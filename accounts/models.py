"""
accounts/models.py

Custom user model for Khoj. Three roles exist:
- FAMILY: Files missing person reports
- HOSPITAL: Uploads unidentified patient records
- POLICE: Explores regional cases as investigation support

Hospital and Police users have extended profile models linked via OneToOne.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Custom manager for KhojUser -> This manager knows how to create KhojUser objects correctly.
# KhojUserManager will use the BLUEPRINT(KhojUser) to create KhojUser instances but validate,hash,save etc all done in KhojUserManager.
class KhojUserManager(BaseUserManager):
    """Custom manager for KhojUser."""

    def create_user(self, email, full_name, role, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email) # lowercase the domain part of the email
        user = self.model(email=email, full_name=full_name, role=role, **extra_fields) # create user instance with help of KhojUser
        # self.model -> points to whichever model the manager is attached to . For now it refers to KhojUser. We used to self.model instead of hardcoding, user = KhojUser(email=email,full_name=full_name,...)
        user.set_password(password)
        user.save(using=self._db) # saving user to DB , and user=self._db is means -> use whichever database is currently configured.
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields): # called when creating a superuser for Django admin
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, role='FAMILY', password=password, **extra_fields)

# Custom user model for Khoj -> THE BLUEPRINT FOR DATABASE USER TABLE to define which fields will be present for user.
class KhojUser(AbstractBaseUser, PermissionsMixin):
    """
    Base user model for Khoj.
    All three role types (Family, Hospital, Police) use this model.
    Hospital and Police have additional profile models for institutional fields.
    """

    ROLE_CHOICES = [
        ('FAMILY', 'Family'),
        ('HOSPITAL', 'Hospital Staff'),
        ('POLICE', 'Police Officer'),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
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

    USERNAME_FIELD = 'email' # making email act as the username throughout Django's auth system
    REQUIRED_FIELDS = ['full_name']

    objects = KhojUserManager() # connecting KhojUserManager to KhojUser i.e, internally its is KhojUserManager.model = KhojUser 

    def __str__(self):
        return f"{self.full_name} ({self.role})"

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
    staff_id acts as their institutional identifier.
    """

    user = models.OneToOneField(KhojUser, on_delete=models.CASCADE, related_name='hospital_profile')
    staff_id = models.CharField(max_length=50, unique=True)
    hospital_registration_id = models.CharField(max_length=100)  # Stored for future verification
    hospital_name = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=10)
    hospital_email = models.EmailField()

    def __str__(self):
        return f"{self.hospital_name} - {self.staff_id}"


class PoliceProfile(models.Model):
    """
    Extended profile for Police users.
    Stores institutional details for the police station.
    police_id acts as their institutional identifier.
    """

    user = models.OneToOneField(KhojUser, on_delete=models.CASCADE, related_name='police_profile')
    police_id = models.CharField(max_length=50, unique=True)
    police_station_registration_id = models.CharField(max_length=100)  # Stored for future verification
    police_station_name = models.CharField(max_length=200)
    district = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.police_station_name} - {self.police_id}"
