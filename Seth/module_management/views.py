import pprint

from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.forms.models import ModelForm
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views import generic

from Grades.models import Module, Module_ed, Course, Test, Person, Coordinator


class IndexView(generic.ListView):
    template_name = 'module_management/index.html'
    context_object_name = 'module_list'

    def get_queryset(self):
        """Return all modules"""
        user = self.request.user
        module_list = Module.objects.prefetch_related('module_ed_set').filter(
            module_ed__module_coordinator__user=user).distinct()
        return module_list

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['mod_eds'] = Module_ed.objects.filter(module_coordinator__user=self.request.user)
        return context

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


class ModuleView(generic.DetailView):
    template_name = 'module_management/module_detail.html'
    model = Module

    def get_context_data(self, **kwargs):
        context = super(ModuleView, self).get_context_data(**kwargs)
        context['mod_eds'] = Module_ed.objects.filter(module_coordinator__user=self.request.user)
        return context

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


class CreateModuleEdForm(ModelForm):
    class Meta:
        model = Module_ed
        fields = ['module', 'module_code_extension', 'start', 'stop', 'year', 'module_coordinator', 'courses']

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['module'].widget.attrs['disabled'] = True
        self.fields['module_coordinator'].widget.attrs['disabled'] = True


class ModuleEdCreateView(generic.CreateView):
    template_name = 'module_management/module_ed_create.html'
    form_class = CreateModuleEdForm

    def get_initial(self):
        pk = self.request.path_info.split('/')[2]
        latest_module_ed = Module_ed.objects.filter(module=pk).latest('year').pk
        return {
            'module': Module.objects.get(pk=pk),
            'module_coordinator': Person.objects.filter(coordinator__module=latest_module_ed)
        }

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.request.path_info.split('/')[2]
        latest_module_ed = Module_ed.objects.filter(module=pk).latest('year').pk

        if not Person.objects.filter(coordinator__module=latest_module_ed).filter(user=user):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        initial = self.get_form_kwargs()['initial']
        data = self.get_form_kwargs()['data']
        pk = request.path_info.split('/')[2]
        latest_module_ed = Module_ed.objects.filter(module=pk).latest('year').pk
        module_ed = Module_ed(
            module=initial['module'],
            module_code_extension=data['module_code_extension'],
            start=data['start'],
            stop=data['stop'],
            year=data['year']
        )
        try:
            module_ed.full_clean()
        except ValidationError as e:
            pp = pprint.PrettyPrinter(indent=4, width=120)
            return HttpResponseBadRequest(pp.pformat(('Form data is invalid: ', e.message_dict)))
        module_ed.save()

        for person in initial['module_coordinator']:
            coordinator = Coordinator(
                module=module_ed,
                person=person,
                mc_assistant=Coordinator.objects.get(person=person, module=latest_module_ed).mc_assistant
            )
            try:
                coordinator.full_clean()
            except ValidationError as e:
                pp = pprint.PrettyPrinter(indent=4, width=120)
                return HttpResponseBadRequest(pp.pformat(('Coordinator is invalid: ', e.message_dict)))
            coordinator.save()

        return redirect('module_management:module_overview')


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
