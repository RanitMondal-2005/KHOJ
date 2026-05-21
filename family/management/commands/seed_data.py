"""
family/management/commands/seed_data.py

Seeds demo accounts so the project can be explored immediately.
Only creates users and institutional profiles — no image-based records,
since those require actual files and are best added through the UI.

Run: python manage.py seed_data
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates demo user accounts for development testing'

    def handle(self, *args, **options):
        from accounts.models import KhojUser, HospitalProfile, PoliceProfile

        self.stdout.write(self.style.MIGRATE_HEADING("Creating demo accounts..."))

        # ── Family User ───────────────────────────────────────────────────────
        family_user, created = KhojUser.objects.get_or_create(email='family@demo.com')
        family_user.full_name = 'Ramesh Sharma'
        family_user.role = 'FAMILY'
        family_user.set_password('demo1234')
        family_user.save()
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status}: Family user — family@demo.com")

        # ── Hospital Staff User ───────────────────────────────────────────────
        hosp_user, created = KhojUser.objects.get_or_create(email='hospital@demo.com')
        hosp_user.full_name = 'Dr. Priya Singh'
        hosp_user.role = 'HOSPITAL'
        hosp_user.set_password('demo1234')
        hosp_user.save()

        HospitalProfile.objects.get_or_create(
            user=hosp_user,
            defaults={
                'staff_id': 'STAFF001',
                'hospital_registration_id': 'HOSP-KOL-001',
                'hospital_name': 'NRS Medical College & Hospital',
                'district': 'Kolkata',
                'address': '138, AJC Bose Road, Kolkata - 700014',
                'emergency_contact': '9800001111',
                'hospital_email': 'nrs@demo.com',
            }
        )
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status}: Hospital user — hospital@demo.com")

        # ── Police User ───────────────────────────────────────────────────────
        pol_user, created = KhojUser.objects.get_or_create(email='police@demo.com')
        pol_user.full_name = 'SI Debashis Roy'
        pol_user.role = 'POLICE'
        pol_user.set_password('demo1234')
        pol_user.save()

        PoliceProfile.objects.get_or_create(
            user=pol_user,
            defaults={
                'police_id': 'WB001234',
                'police_station_registration_id': 'PS-KOL-01',
                'police_station_name': 'Park Street Police Station',
                'district': 'Kolkata',
            }
        )
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status}: Police user — police@demo.com")

        # ── Second Hospital (different district for variety) ──────────────────
        hosp2_user, created = KhojUser.objects.get_or_create(email='hospital2@demo.com')
        hosp2_user.full_name = 'Dr. Souvik Chatterjee'
        hosp2_user.role = 'HOSPITAL'
        hosp2_user.set_password('demo1234')
        hosp2_user.save()

        HospitalProfile.objects.get_or_create(
            user=hosp2_user,
            defaults={
                'staff_id': 'STAFF002',
                'hospital_registration_id': 'HOSP-HWH-001',
                'hospital_name': 'Howrah District Hospital',
                'district': 'Howrah',
                'address': 'Hospital Road, Howrah - 711101',
                'emergency_contact': '9800002222',
                'hospital_email': 'howrahdist@demo.com',
            }
        )
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status}: Hospital2 user — hospital2@demo.com")

        # ── Second Family User ────────────────────────────────────────────────
        fam2_user, created = KhojUser.objects.get_or_create(email='family2@demo.com')
        fam2_user.full_name = 'Sunita Bose'
        fam2_user.role = 'FAMILY'
        fam2_user.set_password('demo1234')
        fam2_user.save()
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status}: Family2 user — family2@demo.com")

        self.stdout.write(self.style.SUCCESS("""
Done! Demo accounts ready.

╔══════════════════════════════════════════════════════════╗
║               KHOJ DEMO LOGIN CREDENTIALS               ║
╠═══════════════════════╦══════════════════╦══════════════╣
║ Role                  ║ Email            ║ Password     ║
╠═══════════════════════╬══════════════════╬══════════════╣
║ Family                ║ family@demo.com  ║ demo1234     ║
║ Family (2nd user)     ║ family2@demo.com ║ demo1234     ║
║ Hospital (Kolkata)    ║ hospital@demo.com║ demo1234     ║
║ Hospital (Howrah)     ║ hospital2@demo.com│ demo1234    ║
║ Police (Kolkata)      ║ police@demo.com  ║ demo1234     ║
╚═══════════════════════╩══════════════════╩══════════════╝

Add missing person reports and patient records through the UI.
Matching runs automatically when records are saved.
"""))
