# meetings/models.py
from django.db import models

class Organizer(models.Model):
    organizer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    industry_type = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return f"ID: {self.organizer_id} - {self.name}"

    class Meta:
        indexes = [
            models.Index(fields=['industry_type'], name='organizer_industry_idx'),
        ]

class Meeting(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateTimeField(db_index=True)
    description = models.TextField()
    mandatory = models.BooleanField(default=False, db_index=True)
    organizers = models.ManyToManyField(Organizer, through='MeetingOrganizer', blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['date', 'mandatory'], name='meeting_date_mandatory_idx'),
        ]

    def __str__(self):
        return self.title

class MeetingOrganizer(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    organizer = models.ForeignKey(
        Organizer, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    class Meta:
        unique_together = ['meeting', 'organizer']
        indexes = [
            models.Index(fields=['meeting', 'organizer'], name='meeting_organizer_idx'),
        ]

    def __str__(self):
        return f"{self.meeting.title} - {self.organizer.name if self.organizer else 'No organizer'}"
