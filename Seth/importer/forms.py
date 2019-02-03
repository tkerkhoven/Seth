from django import forms
from django.core.validators import FileExtensionValidator

from Grades.models import Test, ModulePart


COLUMN_TITLE_ROW = 5  # title-row, zero-indexed, that contains the title for the grade sheet rows.


class GradeUploadForm(forms.Form):
    title_row = forms.IntegerField(
        label='Title row (starting from 1)',
        initial=COLUMN_TITLE_ROW+1,
        min_value=1
    )
    file = forms.FileField(
        label='Select the graded excel file',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xls', 'xlsx'])]
    )


class TestGradeUploadForm(forms.Form):
    title_row = forms.IntegerField(
        label='Title row (starting from 1)',
        initial=COLUMN_TITLE_ROW+1,
        min_value=1
    )
    file = forms.FileField(
        label='Select the graded excel file',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xls', 'xlsx'])]
    )


class ImportModuleForm(forms.Form):
    title_row = forms.IntegerField(
        label='Title row (starting from 1)',
        initial=COLUMN_TITLE_ROW+1,
        min_value=1
    )
    file = forms.FileField(
        label='Select the graded excel (or CSV) file',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xls', 'xlsx'])]
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