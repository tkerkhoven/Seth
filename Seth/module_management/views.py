from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.views import generic

from Grades.models import Module, Module_ed, Course, Test


class IndexView(generic.ListView):
    template_name = 'module_management/index2.html'
    context_object_name = 'module_list'

    def get_queryset(self):
        """Return all modules"""
        user = self.request.user
        module_list = Module.objects.prefetch_related('module_ed_set').filter(module_ed__module_coordinator__user=user)
        return module_list

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not Module_ed.objects.filter(module_coordinator__user=user):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


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


class CourseView(generic.DetailView):
    template_name = 'module_management/course_detail.html'
    model = Course

    def dispatch(self, request, *args, **kwargs):
        pk = request.path_info.split('/')[2]
        user = request.user

        if not Course.objects.filter(Q(pk=pk) & (Q(module_ed__module_coordinator__user=user) | Q(teachers__user=user))):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class TestView(generic.DetailView):
    template_name = 'module_management/test_detail.html'
    model = Test

    def dispatch(self, request, *args, **kwargs):
        pk = request.path_info.split('/')[2]
        user = request.user
        if not Test.objects.filter(Q(pk=pk) & (
                    Q(course_id__module_ed__module_coordinator__user=user) | Q(course_id__teachers__user=user))):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class ModuleEdUpdateView(generic.UpdateView):
    template_name = 'module_management/module_ed_update.html'
    model = Module_ed
    fields = ['year', 'module_code_extension', 'courses', 'start', 'stop']

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


class CourseUpdateView(generic.UpdateView):
    template_name = 'module_management/course_update.html'
    model = Course
    fields = ['code', 'code_extension', 'teachers', 'name']

    def dispatch(self, request, *args, **kwargs):
        pk = request.path_info.split('/')[2]
        user = request.user

        if not Course.objects.filter(Q(pk=pk) & (Q(module_ed__module_coordinator__user=user) | Q(teachers__user=user))):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class TestUpdateView(generic.UpdateView):
    template_name = 'module_management/test_update.html'
    model = Test
    fields = ['name', '_type', 'time', 'maximum_grade', 'minimum_grade']

    def dispatch(self, request, *args, **kwargs):
        pk = request.path_info.split('/')[2]
        user = request.user
        if not Test.objects.filter(Q(pk=pk) & (
                    Q(course_id__module_ed__module_coordinator__user=user) | Q(course_id__teachers__user=user))):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
