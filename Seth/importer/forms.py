from django import forms

from Grades.models import Test, Course

class GradeUploadForm(forms.Form):
    test = forms.ModelChoiceField(queryset=Test.objects.all(), label='Test to register grades for', to_field_name="pk")
    file = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )