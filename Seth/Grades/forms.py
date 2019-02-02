from django.forms import ModelForm, CharField, EmailField, Field
from django_select2.forms import Select2Widget

from Grades.models import Studying


class StudyingCreateForm(ModelForm):
    class Meta:
        model = Studying
        fields = ['person']
        widgets = {'person': Select2Widget}

    def __init__(self, *args, **kwargs):
        super(StudyingCreateForm, self).__init__(*args, **kwargs)
        self.fields['person'].required = False
        self.fields['person'].label = 'Find a student by name'
        self.fields['just_text'] = Field(label='Or fill in the full name, student number and email below.',
                                         disabled=True, required=False)
        self.fields['new_name'] = CharField(label='Full Name', required=False)
        self.fields['new_number'] = CharField(label='Student Number (with s)', required=False)
        self.fields['new_email'] = EmailField(label='Student Email', required=False)
        self.fields['role'] = CharField(label='Role of the student in this module', required=False)
