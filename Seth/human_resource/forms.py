from django import forms

from django.contrib.auth.models import User
from Grades.models import Person, Teacher, ModulePart


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', "university_number", 'email']


class CreateUserForm(forms.Form):
    teacher_role_choices = ['---------', 'Teacher', 'Teaching Assistant']
    name = forms.CharField(label='Name', max_length=255)
    university_number = forms.CharField(label='University number', max_length=16)
    email_address = forms.EmailField(label='Email address')
    user = forms.ModelChoiceField(queryset=User.objects.all())
    create_teacher = forms.BooleanField(required=False)
    role_teacher = forms.ChoiceField(choices=Teacher.ROLES, label='Role', required=False)
    module_part_teacher = forms.ModelChoiceField(queryset=ModulePart.objects.all(), label='Module part', required=False)
