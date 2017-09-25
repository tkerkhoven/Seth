from django import forms

from Grades.models import Test, Course

class GradeUploadForm(forms.Form):

    def __init__(self, pk, post=None, files=None):
        if post is not None:
            super(GradeUploadForm, self).__init__(post, files)
        else:
            super(GradeUploadForm, self).__init__()
        self.fields['test'] = forms.ModelChoiceField(queryset=Test.objects.filter(course_id__module_ed__pk=pk),
                                                     label='Test to register grades for', to_field_name="pk")

    test = forms.ModelChoiceField(queryset=Test.objects.all(), label='Test to register grades for', to_field_name="pk")
    file = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )