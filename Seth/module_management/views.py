from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views import generic

from Grades.models import Module, Module_ed


def is_module_coordinator_check(user):
    if not Module_ed.objects.filter(module_coordinator__user=user):
        return False
    else:
        return True


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_module_coordinator_check), name='dispatch')
class IndexView(generic.ListView):
    template_name = 'module_management/index.html'
    context_object_name = 'module_list'

    def get_queryset(self):
        """Return all modules"""
        user = self.request.user
        module_list = Module.objects.prefetch_related('module_ed_set').filter(module_ed__module_coordinator__user=user)
        return module_list


class ModuleEdView(generic.DetailView):
    template_name = 'module_management/module_ed_detail.html'
    model = Module_ed

    def dispatch(self, request, *args, **kwargs):
        pk = request.path_info.split('/')[2]
        user = request.user

        if not Module_ed.objects.filter(module_coordinator__user=user).filter(pk=pk):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class ModuleView(generic.DetailView):
    template_name = 'module_management/module_detail.html'
    model = Module

    def dispatch(self, request, *args, **kwargs):
        pk = request.path_info.split('/')[2]
        user = request.user

        if not Module.objects.filter(pk=pk).filter(module_ed__module_coordinator__user=user):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
