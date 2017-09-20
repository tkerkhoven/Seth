from django.shortcuts import render
from django.views import generic
from Grades.models import Module_ed

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'importer/'
    model = Module_ed

    def get_queryset(self):
        Module_ed.objects.order_by('start')