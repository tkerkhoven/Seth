from django import forms

from Grades.models import Test, Course


class GradeUploadForm(forms.Form):
    file = forms.FileField(
        label='Select the graded excel file',
    )


class TestGradeUploadForm(forms.Form):
    file = forms.FileField(
        label='Select the graded excel file',
    )


class ImportStudentForm(forms.Form):
    file = forms.FileField(
        label='Select Student excel file'
    )
