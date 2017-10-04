import pprint

from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.db.transaction import set_autocommit, rollback, commit
from django.forms.models import ModelForm
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import ModelFormMixin

from Grades.models import Module, ModuleEdition, ModulePart, Test, Person, Coordinator, Teacher, Grade, Studying


class IndexView(generic.ListView):
    template_name = 'module_management/index2.html'
    context_object_name = 'module_list'

    def get_queryset(self):
        user = self.request.user
        module_list = Module.objects.prefetch_related('module_ed_set').filter(
            module_ed__module_coordinator__user=user).distinct()
        return module_list

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['mod_eds'] = ModuleEdition.objects.filter(module_coordinator__user=self.request.user)
        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not ModuleEdition.objects.filter(module_coordinator__user=user):
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
        context['mod_eds'] = ModuleEdition.objects.filter(module_coordinator__user=self.request.user)
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
    model = ModuleEdition

    def dispatch(self, request, *args, **kwargs):
        pk = request.path_info.split('/')[2]
        user = request.user

        if not ModuleEdition.objects.filter(module_coordinator__user=user).filter(pk=pk):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ModuleEdView, self).get_context_data(**kwargs)
        studying = Studying.objects.filter(module_id=self.kwargs['pk']).prefetch_related('person').prefetch_related(
            'study')

        context['studying'] = studying
        print(context)
        return context


class ModuleEdUpdateView(generic.UpdateView):
    template_name = 'module_management/module_ed_update.html'
    model = ModuleEdition
    fields = ['year', 'block', 'start', 'stop']

    def dispatch(self, request, *args, **kwargs):
        pk = request.path_info.split('/')[2]
        user = request.user

        if not ModuleEdition.objects.filter(module_coordinator__user=user).filter(pk=pk):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class ModuleEdCreateForm(ModelForm):
    class Meta:
        model = ModuleEdition
        fields = ['module', 'start', "end", 'year', "coordinators"]

    def __init__(self, *args, **kwargs):
        super(ModuleEdCreateForm, self).__init__(*args, **kwargs)
        self.fields['module'].widget.attrs['disabled'] = True
        self.fields['module_coordinator'].widget.attrs['disabled'] = True


class ModuleEdCreateView(generic.CreateView):
    template_name = 'module_management/module_ed_create.html'
    form_class = ModuleEdCreateForm

    def get_initial(self):
        pk = self.request.path_info.split('/')[2]
        latest_module_ed = ModuleEdition.objects.filter(module=pk).latest('year').pk
        return {
            'module': Module.objects.get(pk=pk),
            'module_coordinator': Person.objects.filter(coordinator__module=latest_module_ed)
        }

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.request.path_info.split('/')[2]
        latest_module_ed = ModuleEdition.objects.filter(module=pk).latest('year').pk

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
        latest_module_ed = ModuleEdition.objects.filter(module=pk).latest('year').pk

        set_autocommit(False)

        module_ed = ModuleEdition(
            module=initial['module'],
            start=data['start'],
            stop=data['stop'],
            year=data['year']
        )
        try:
            module_ed.full_clean()
        except ValidationError as e:
            pp = pprint.PrettyPrinter(indent=4, width=120)
            rollback()
            set_autocommit(True)
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
                rollback()
                set_autocommit(True)
                return HttpResponseBadRequest(pp.pformat(('Coordinator is invalid: ', e.message_dict)))
            coordinator.save()

        commit()
        set_autocommit(True)
        return redirect('module_management:module_overview')


class CourseView(generic.DetailView):
    template_name = 'module_management/course_detail.html'
    model = ModulePart

    def get_context_data(self, **kwargs):
        context = super(CourseView, self).get_context_data(**kwargs)
        module_eds = ModuleEdition.objects.filter(courses__id=self.kwargs['pk'])
        print(module_eds)
        studying = Studying.objects.filter(module_id__in=module_eds).prefetch_related('person').prefetch_related(
            'study')
        print(studying)
        context['studying'] = studying
        return context

    def dispatch(self, request, *args, **kwargs):
        pk = request.path_info.split('/')[2]
        user = request.user

        if not ModulePart.objects.filter(
                        Q(pk=pk) & (Q(module_ed__module_coordinator__user=user) | Q(teachers__user=user))):
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
    model = ModulePart
    fields = ['teachers', 'name']

    def dispatch(self, request, *args, **kwargs):
        pk = request.path_info.split('/')[2]
        user = request.user

        if not ModulePart.objects.filter(Q(pk=pk) & (Q(module_ed__module_coordinator__user=user))):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        Teacher.objects.filter(course=self.object).delete()
        for t in form.cleaned_data['teachers']:
            teacher = Teacher()
            teacher.module_part = self.object
            teacher.person = t
            if t.univserity_number[0] == 'm':
                teacher.role = 'T'
            else:
                teacher.role = 'A'
            teacher.save()
        return super(ModelFormMixin, self).form_valid(form)


class CourseCreateForm(ModelForm):
    class Meta:
        model = ModulePart
        fields = ['name', 'teachers']


class CourseCreateView(generic.CreateView):
    template_name = 'module_management/course_create.html'
    form_class = CourseCreateForm

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.request.path_info.split('/')[2]

        if not Person.objects.filter(coordinator__module=pk).filter(user=user):
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
        data = self.get_form_kwargs()['data']
        pk = request.path_info.split('/')[2]

        set_autocommit(False)

        course = ModulePart(
            name=data['name']
        )
        try:
            course.full_clean()
        except ValidationError as e:
            pp = pprint.PrettyPrinter(indent=4, width=120)
            rollback()
            set_autocommit(True)
            return HttpResponseBadRequest(pp.pformat(('Form data is invalid: ', e.message_dict)))
        course.save()

        module_ed = ModuleEdition.objects.get(pk=pk)
        module_ed.courses.add(course)
        try:
            module_ed.full_clean()
        except ValidationError as e:
            pp = pprint.PrettyPrinter(indent=4, width=120)
            rollback()
            set_autocommit(True)
            return HttpResponseBadRequest(pp.pformat(('Module Edition is invalid: ', e.message_dict)))
        module_ed.save()

        for t in data.getlist('teachers'):
            t = Person.objects.get(pk=t)
            if t.univserity_number[0] == 'm':
                role = 'T'
            else:
                role = 'A'
            teacher = Teacher(
                course=course,
                person=t,
                role=role
            )
            try:
                teacher.full_clean()
            except ValidationError as e:
                pp = pprint.PrettyPrinter(indent=4, width=120)
                rollback()
                set_autocommit(True)
                return HttpResponseBadRequest(pp.pformat(('Teacher is invalid: ', e.message_dict)))
            teacher.save()

        commit()
        set_autocommit(True)
        return redirect(reverse_lazy('module_management:module_ed_detail', kwargs={'pk': pk}))


class CourseDeleteView(generic.DeleteView):
    model = ModulePart
    template_name = 'module_management/course_delete.html'
    success_url = reverse_lazy('module_management:module_overview')

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.request.path_info.split('/')[2]

        if Grade.objects.filter(test_id__course_id=pk):
            raise PermissionDenied('Cannot remove a course that has grades')

        if not ModulePart.objects.filter(Q(pk=pk) & (Q(module_ed__module_coordinator__user=user))):
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


class TestCreateForm(ModelForm):
    class Meta:
        model = Test
        fields = ["module_part", 'name', "type", 'time', 'maximum_grade', 'minimum_grade']

    def __init__(self, *args, **kwargs):
        super(TestCreateForm, self).__init__(*args, **kwargs)
        self.fields['course_id'].widget.attrs['disabled'] = True


class TestCreateView(generic.CreateView):
    template_name = 'module_management/test_create.html'
    form_class = TestCreateForm

    def get_initial(self):
        pk = self.request.path_info.split('/')[2]
        return {
            'course_id': ModulePart.objects.get(pk=pk)
        }

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.request.path_info.split('/')[2]

        if not ModulePart.objects.filter(Q(pk=pk) & (Q(module_ed__module_coordinator__user=user))):
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

        set_autocommit(False)

        test = Test(
            course_id=initial['course_id'],
            name=data['name'],
            _type=data['_type'],
            time=data['time'],
            maximum_grade=data['maximum_grade'],
            minimum_grade=data['minimum_grade']
        )
        try:
            test.full_clean()
        except ValidationError as e:
            pp = pprint.PrettyPrinter(indent=4, width=120)
            rollback()
            set_autocommit(True)
            return HttpResponseBadRequest(pp.pformat(('Form data is invalid: ', e.message_dict)))
        test.save()

        commit()
        set_autocommit(True)
        return redirect(reverse_lazy('module_management:course_detail', kwargs={'pk': pk}))


class TestDeleteView(generic.DeleteView):
    model = Test
    template_name = 'module_management/test_delete.html'
    success_url = reverse_lazy('module_management:module_overview')

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.request.path_info.split('/')[2]

        if Grade.objects.filter(test_id=pk):
            raise PermissionDenied('Cannot remove a test that has grades')

        if not Test.objects.filter(Q(pk=pk) & (Q(course_id__module_ed__module_coordinator__user=user))):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
