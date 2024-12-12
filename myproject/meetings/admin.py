# meetings/admin.py
from django.contrib import admin
from .models import Meeting, Organizer, MeetingOrganizer

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'mandatory']

@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ['organizer_id', 'name', 'industry_type']

@admin.register(MeetingOrganizer)
class MeetingOrganizerAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'organizer']
