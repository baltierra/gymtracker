
from django import forms
from .models import DayPlan
class DaySelectForm(forms.Form):
    day=forms.ChoiceField(choices=DayPlan._meta.get_field('day').choices)
