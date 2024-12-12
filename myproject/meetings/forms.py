# meetings/forms.py
from django import forms
from .models import Meeting, Organizer, MeetingOrganizer

class OrganizerForm(forms.ModelForm):
    class Meta:
        model = Organizer
        fields = ['name', 'industry_type']

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'date', 'description', 'mandatory', 'organizers']
        widgets = {
            'organizers': forms.SelectMultiple(attrs={'class': 'organizer-select'}),
            'mandatory': forms.CheckboxInput(attrs={'class': 'checkbox-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organizers'].queryset = Organizer.objects.all()
        self.fields['organizers'].label_from_instance = lambda obj: f"ID: {obj.organizer_id} - {obj.name}"

class MeetingOrganizerForm(forms.ModelForm):
    class Meta:
        model = MeetingOrganizer
        fields = ['organizer']

class ReportForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    mandatory_only = forms.BooleanField(required=False)
    organizer = forms.ModelChoiceField(
        queryset=Organizer.objects.all(),
        required=False,
        empty_label="All Organizers"
    )
    industry_type = forms.ChoiceField(
        choices=[('', 'All Industries')] + [
            (choice, choice) for choice in 
            Organizer.objects.values_list('industry_type', flat=True).distinct()
        ],
        required=False
    )
