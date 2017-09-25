from django import forms
from .models import Person
from django.forms.formsets import formset_factory


class ActionForm(forms.Form):
    CHOICES = (('-----', ' ----- '),('release', 'Release Grades'),('retract', 'Retract Grades'))
    action = forms.ChoiceField(choices=CHOICES)

class ReleaseForm(forms.Form):
    grade = forms.BooleanField(required=False)

    def clean_grade(self):
        grade = self.cleaned_data['grade']
        return grade

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'id_prefix', 'person_id', 'start', 'stop', 'role', 'studies']