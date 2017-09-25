from django import forms

from Grades.models import Test, Course

class GradeUploadForm(forms.Form):

    def __init__(self, pk):
        super(GradeUploadForm, self).__init__()
        self.fields['test'] = forms.ModelChoiceField(queryset=Test.objects.filter(course_id__module_ed__pk=pk), label='Test to register grades for', to_field_name="pk")

    def __init__(self, pk, post, files):
        super(GradeUploadForm, self).__init__(post, files)
        self.fields['test'] = forms.ModelChoiceField(queryset=Test.objects.filter(course_id__module_ed__pk=pk),
                                                     label='Test to register grades for', to_field_name="pk")

    test = forms.ModelChoiceField(queryset=Test.objects.all(), label='Test to register grades for', to_field_name="pk")
    file = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )