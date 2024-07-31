from .models import Event_booking 
from django import forms




class EventForm(forms.ModelForm):
    class Meta:
        model = Event_booking
        fields = ['name', 'start_time', 'end_time', 'date_start', 'date_end', 'category']