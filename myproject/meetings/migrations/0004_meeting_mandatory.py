# Generated by Django 5.1 on 2024-11-03 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0003_remove_meetingorganizer_student_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='mandatory',
            field=models.BooleanField(default=False),
        ),
    ]
