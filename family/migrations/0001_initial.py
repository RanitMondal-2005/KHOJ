"""family/migrations/0001_initial.py"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MissingPerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person_name', models.CharField(max_length=150)),
                ('age', models.PositiveIntegerField()),
                ('gender', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')], max_length=10)),
                ('height', models.PositiveIntegerField(help_text='Height in cm')),
                ('weight', models.PositiveIntegerField(help_text='Weight in kg')),
                ('blood_group', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'), ('UNKNOWN', 'Unknown')], default='UNKNOWN', max_length=10)),
                ('eye_color', models.CharField(max_length=50)),
                ('hair_color', models.CharField(max_length=50)),
                ('skin_tone', models.CharField(choices=[('FAIR', 'Fair'), ('WHEATISH', 'Wheatish'), ('MEDIUM', 'Medium'), ('DARK', 'Dark'), ('UNKNOWN', 'Unknown')], default='UNKNOWN', max_length=20)),
                ('identifying_marks', models.TextField(blank=True, help_text='Scars, tattoos, birthmarks, etc.')),
                ('clothing_description', models.TextField(blank=True, help_text='What they were last wearing')),
                ('last_seen_location', models.CharField(max_length=255)),
                ('district', models.CharField(max_length=100)),
                ('last_seen_date', models.DateField()),
                ('passport_photo', models.ImageField(upload_to='missing/passport/')),
                ('full_body_photo', models.ImageField(upload_to='missing/fullbody/')),
                ('contact_number', models.CharField(max_length=15)),
                ('fir_number', models.CharField(blank=True, help_text='FIR number if filed', max_length=100)),
                ('police_station_name', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('FOUND', 'Found'), ('CLOSED', 'Closed')], default='ACTIVE', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('linked_family_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='missing_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CaseUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField(help_text='Search progress, clue, or new information')),
                ('optional_image', models.ImageField(blank=True, null=True, upload_to='updates/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('linked_missing_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='case_updates', to='family.missingperson')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
