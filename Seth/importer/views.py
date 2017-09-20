from django.shortcuts import render
from django.views import generic
from Grades.models import Module_ed

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'importer/index.html'
    model = Module_ed

    def get_queryset(self):
        return Module_ed.objects.order_by('start')

class ImportModuleView(generic.ListView):
    template_name = 'importer/importmodule.html'
    model = Module_ed

    def get_queryset(self):
        return Module_ed.objects.order_by('start')