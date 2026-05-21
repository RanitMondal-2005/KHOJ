"""hospital/migrations/0001_initial.py"""

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
            name='UnidentifiedPatient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estimated_name', models.CharField(blank=True, help_text='If any name was found or given', max_length=150)),
                ('age', models.PositiveIntegerField(help_text='Estimated age')),
                ('gender', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other'), ('UNKNOWN', 'Unknown')], default='UNKNOWN', max_length=10)),
                ('height', models.PositiveIntegerField(help_text='Estimated height in cm')),
                ('weight', models.PositiveIntegerField(help_text='Estimated weight in kg')),
                ('blood_group', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'), ('UNKNOWN', 'Unknown')], default='UNKNOWN', max_length=10)),
                ('eye_color', models.CharField(blank=True, max_length=50)),
                ('hair_color', models.CharField(blank=True, max_length=50)),
                ('skin_tone', models.CharField(choices=[('FAIR', 'Fair'), ('WHEATISH', 'Wheatish'), ('MEDIUM', 'Medium'), ('DARK', 'Dark'), ('UNKNOWN', 'Unknown')], default='UNKNOWN', max_length=20)),
                ('identifying_marks', models.TextField(blank=True, help_text='Any visible marks, scars, tattoos')),
                ('found_location', models.CharField(max_length=255)),
                ('district', models.CharField(max_length=100)),
                ('condition_notes', models.TextField(blank=True, help_text='Medical condition, mental state on arrival, etc.')),
                ('face_image', models.ImageField(upload_to='patients/face/')),
                ('full_body_image', models.ImageField(upload_to='patients/fullbody/')),
                ('side_profile_image', models.ImageField(upload_to='patients/side/')),
                ('admission_date', models.DateField()),
                ('status', models.CharField(choices=[('UNIDENTIFIED', 'Unidentified'), ('IDENTIFIED', 'Identified')], default='UNIDENTIFIED', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('linked_hospital', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_records', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
