"""matching/migrations/0001_initial.py"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('family', '0001_initial'),
        ('hospital', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confidence_score', models.FloatField(help_text='Score out of 100')),
                ('status', models.CharField(choices=[('PENDING', 'Pending Review'), ('VERIFIED', 'Verified'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('missing_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='family.missingperson')),
                ('unidentified_patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='hospital.unidentifiedpatient')),
            ],
            options={
                'ordering': ['-confidence_score'],
                'unique_together': {('missing_person', 'unidentified_patient')},
            },
        ),
    ]
