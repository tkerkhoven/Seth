from django.forms import Form, Textarea
from django import forms


class EmailPreviewForm(Form):
    subject = forms.CharField(initial="Your subject here", max_length=255)
    message = forms.CharField(initial="Your message here", max_length=10000, widget=Textarea(attrs={'cols': 80, 'rows': 20}))

