from django import forms

from Grades.models import Test, ModulePart


class GradeUploadForm(forms.Form):
    title_row = forms.IntegerField(
        label='Title row (starting from 1)',
        initial=COLUMN_TITLE_ROW+1,
        min_value=1
    )
    file = forms.FileField(
        label='Select the graded excel file',
    )


class TestGradeUploadForm(forms.Form):
    title_row = forms.IntegerField(
        label='Title row (starting from 1)',
        initial=COLUMN_TITLE_ROW+1,
        min_value=1
    )
    file = forms.FileField(
        label='Select the graded excel file',
    )


class ImportStudentForm(forms.Form):
    file = forms.FileField(
        label='Select Student excel file'
    )


class ImportStudentModule(forms.Form):
    file = forms.FileField(
        label='Select Student excel file'
    )
class ImportModuleEditionStructureForm(forms.Form):
    file = forms.FileField(
        label='Select module structure excel file'
    )