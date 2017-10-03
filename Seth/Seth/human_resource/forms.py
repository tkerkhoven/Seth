from django import forms
from Grades.models import Person

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'id_prefix', 'person_id', 'start', 'stop',]