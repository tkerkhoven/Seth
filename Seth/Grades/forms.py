from django import forms
from .models import Person

class ReleaseForm(forms.Form):
    grade = forms.BooleanField(required=False)

    def clean_grade(self):
        grade = self.cleaned_data['email']
        return grade

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'id_prefix', 'person_id', 'start', 'stop', ]
