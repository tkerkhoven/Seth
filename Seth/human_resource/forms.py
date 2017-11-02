from django import forms

from django.contrib.auth.models import User
from django_select2.forms import Select2MultipleWidget

from Grades.models import Person, Teacher, ModulePart


class UpdatePersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', "university_number", 'email']


class CreatePersonForm(forms.Form):
    name = forms.CharField(label='Name', max_length=255)
    university_number = forms.CharField(label='University number', max_length=16)
    email_address = forms.EmailField(label='Email address')

class CreatePersonTeacherForm(forms.Form):
    teacher_role_choices = ['---------', 'Teacher', 'Teaching Assistant']
    name = forms.CharField(label='Name', max_length=255)
    university_number = forms.CharField(label='University number', max_length=16)
    email_address = forms.EmailField(label='Email address')
    create_teacher = forms.BooleanField(required=False)
    role_teacher = forms.ChoiceField(choices=Teacher.ROLES, label='Role', required=False)
    module_part_teacher = forms.ModelMultipleChoiceField(queryset=ModulePart.objects.all(), label='Module part', required=False, widget=Select2MultipleWidget)
