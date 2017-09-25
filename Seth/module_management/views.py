from django.views import generic

from Grades.models import Module


class IndexView(generic.ListView):
    template_name = 'module_management/index.html'
    context_object_name = 'module_list'

    def get_queryset(self):
        """Return all modules"""
        module_set = Module.objects.prefetch_related('module_ed_set')
        return module_set
