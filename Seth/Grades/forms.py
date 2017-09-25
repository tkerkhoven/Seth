from django import forms

class ReleaseForm(forms.Form):
    grade = forms.BooleanField(required=False)

    def clean_grade(self):
        grade = self.cleaned_data['email']
        return grade