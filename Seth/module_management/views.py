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


class ModuleListView(generic.ListView):
    template_name = 'module_management/module_overview2.html'
    context_object_name = 'module_list'

    def get_queryset(self):
        user = self.request.user
        module_list = Module.objects.prefetch_related('moduleedition_set').filter(moduleedition__coordinators__user=user).distinct()
        return module_list

    def get_context_data(self, **kwargs):
        context = super(ModuleListView, self).get_context_data(**kwargs)
        user = self.request.user
        context['mod_eds'] = ModuleEdition.objects.filter(coordinators__user=user)
        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not ModuleEdition.objects.filter(coordinators__user=user):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class ModuleDetailView(generic.DetailView):
    template_name = 'module_management/module_detail.html'
    model = Module

    def get_context_data(self, **kwargs):
        context = super(ModuleDetailView, self).get_context_data(**kwargs)
        user = self.request.user
        context['module_editions'] = ModuleEdition.objects.filter(coordinators__user=user)
        return context

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = request.user

        if not Module.objects.filter(pk=pk).filter(moduleedition__coordinators__user=user):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class ModuleEditionDetailView(generic.DetailView):
    template_name = 'module_management/module_edition_detail.html'
    model = ModuleEdition

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = request.user

        if not ModuleEdition.objects.filter(coordinators__user=user).filter(pk=pk):
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
        context = super(ModuleEditionDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        studying = Studying.objects.filter(module_edition=pk).prefetch_related('person').prefetch_related('study')
        context['studying'] = studying
        return context


class ModuleEditionUpdateView(generic.UpdateView):
    template_name = 'module_management/module_edition_update.html'
    model = ModuleEdition
    fields = ['year', 'block', 'start', 'end', 'modulepart']

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = request.user

        if not ModuleEdition.objects.filter(coordinators__user=user).filter(pk=pk):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class ModuleEditionCreateForm(ModelForm):
    class Meta:
        model = ModuleEdition
        fields = ['module', 'year', 'block', 'start', 'end', 'coordinators']

    def __init__(self, *args, **kwargs):
        super(ModuleEditionCreateForm, self).__init__(*args, **kwargs)
        self.fields['module'].widget.attrs['disabled'] = True
        self.fields['coordinators'].widget.attrs['disabled'] = True


class ModuleEditionCreateView(generic.CreateView):
    template_name = 'module_management/module_edition_create.html'
    form_class = ModuleEditionCreateForm

    def get_initial(self):
        pk = self.kwargs['pk']
        latest_module_edition = ModuleEdition.objects.filter(module=pk).latest('start').pk
        return {
            'module': Module.objects.get(pk=pk),
            'module_coordinator': Person.objects.filter(coordinator__module=latest_module_edition)
        }

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.kwargs['pk']
        latest_module_edition = ModuleEdition.objects.filter(module=pk).latest('start').pk

        if not Person.objects.filter(coordinator__module=latest_module_edition).filter(user=user):
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
        pk = self.kwargs['pk']
        latest_module_edition = ModuleEdition.objects.filter(module=pk).latest('year')

        set_autocommit(False)

        module_edition = ModuleEdition(
            module=initial['module'],
            start=data['start'],
            end=data['end'],
            year=data['year'],
        )

        try:
            module_edition.full_clean()
        except ValidationError as e:
            pp = pprint.PrettyPrinter(indent=4, width=120)
            rollback()
            set_autocommit(True)
            return HttpResponseBadRequest(pp.pformat(('Form data is invalid: ', e.message_dict)))
        module_edition.save()

        for old_module_part in latest_module_edition.modulepart_set:
            module_part = ModulePart(
                module_edition=module_edition.pk,
                name=old_module_part.name
            )
            try:
                module_part.full_clean()
            except ValidationError as e:
                pp = pprint.PrettyPrinter(indent=4, width=120)
                rollback()
                set_autocommit(True)
                return HttpResponseBadRequest(pp.pformat(('Module Part is invalid: ', e.message_dict)))
            module_part.save()

            for old_test in old_module_part.test_set:
                test = Test(
                    maximum_grade=old_test.maximum_grade,
                    minimum_grade=old_test.minimum_grade,
                    module_part=module_part,
                    name=old_test.name,
                    released=False,
                    time=old_test.time,
                    type=old_test.type
                )
                try:
                    test.full_clean()
                except ValidationError as e:
                    pp = pprint.PrettyPrinter(indent=4, width=120)
                    rollback()
                    set_autocommit(True)
                    return HttpResponseBadRequest(pp.pformat(('Test is invalid: ', e.message_dict)))
                test.save()

        for person in initial['coordinators']:
            coordinator = Coordinator(
                module=module_edition,
                person=person,
                is_assistant=Coordinator.objects.get(person=person, module=latest_module_edition.pk).is_assistant
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


class ModulePartDetailView(generic.DetailView):
    template_name = 'module_management/module_part_detail.html'
    model = ModulePart

    def get_context_data(self, **kwargs):
        context = super(ModulePartDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        module_eds = ModuleEdition.objects.filter(modulepart=pk)
        studying = Studying.objects.filter(module_edition__in=module_eds).prefetch_related('person').prefetch_related('study')
        context['studying'] = studying
        return context

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = request.user

        if not ModulePart.objects.filter(
                        Q(pk=pk) & (Q(module_edition__coordinators__user=user) | Q(teachers__user=user))):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class ModulePartUpdateView(generic.UpdateView):
    template_name = 'module_management/module_part_update.html'
    model = ModulePart
    fields = ['teachers', 'name']

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = request.user

        if not ModulePart.objects.filter(Q(pk=pk) & (Q(module_edition__coordinators__user=user))):
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
        Teacher.objects.filter(module_part=self.object).delete()
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


class ModulePartCreateForm(ModelForm):
    class Meta:
        model = ModulePart
        fields = ['name', 'teachers']


class ModulePartCreateView(generic.CreateView):
    template_name = 'module_management/module_part_create.html'
    form_class = ModulePartCreateForm

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.kwargs['pk']

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
        pk = self.kwargs['pk']

        set_autocommit(False)

        module_part = ModulePart(
            name=data['name'],
            module_edition=pk
        )
        try:
            module_part.full_clean()
        except ValidationError as e:
            pp = pprint.PrettyPrinter(indent=4, width=120)
            rollback()
            set_autocommit(True)
            return HttpResponseBadRequest(pp.pformat(('Form data is invalid: ', e.message_dict)))
        module_part.save()

        # module_edition = ModuleEdition.objects.get(pk=pk)
        # module_edition.courses.add(module_part)
        # try:
        #     module_edition.full_clean()
        # except ValidationError as e:
        #     pp = pprint.PrettyPrinter(indent=4, width=120)
        #     rollback()
        #     set_autocommit(True)
        #     return HttpResponseBadRequest(pp.pformat(('Module Edition is invalid: ', e.message_dict)))
        # module_edition.save()

        for t in data.getlist('teachers'):
            t = Person.objects.get(pk=t)
            if t.univserity_number[0] == 'm':
                role = 'T'
            else:
                role = 'A'
            teacher = Teacher(
                module_part=module_part,
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
        return redirect(reverse_lazy('module_management:module_edition_detail', kwargs={'pk': pk}))


class ModulePartDeleteView(generic.DeleteView):
    model = ModulePart
    template_name = 'module_management/module_part_delete.html'
    success_url = reverse_lazy('module_management:module_overview')

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.kwargs['pk']

        if Grade.objects.filter(test__module_part=pk):
            raise PermissionDenied('Cannot remove a course that has grades')

        if not ModulePart.objects.filter(Q(pk=pk) & (Q(module_edition__coordinators__user=user))):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class TestDetailView(generic.DetailView):
    template_name = 'module_management/test_detail.html'
    model = Test

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = request.user
        if not Test.objects.filter(Q(pk=pk) & (Q(module_part__module_edition__coordinators__user=user) | Q(module_part__teachers__user=user))):
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
    fields = ['name', 'type', 'time', 'maximum_grade', 'minimum_grade']

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = request.user
        if not Test.objects.filter(Q(pk=pk) & (Q(module_part__module_edition__coordinators__user=user) | Q(module_part__teachers__user=user))):
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
        fields = ['module_part', 'name', 'type', 'time', 'maximum_grade', 'minimum_grade']

    def __init__(self, *args, **kwargs):
        super(TestCreateForm, self).__init__(*args, **kwargs)
        self.fields['module_part'].widget.attrs['disabled'] = True


class TestCreateView(generic.CreateView):
    template_name = 'module_management/test_create.html'
    form_class = TestCreateForm

    def get_initial(self):
        pk = self.kwargs['pk']
        return {
            'module_part': ModulePart.objects.get(pk=pk)
        }

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.kwargs['pk']

        if not ModulePart.objects.filter(Q(pk=pk) & (Q(module_edition__coordinators__user=user))):
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
        pk = self.kwargs['pk']

        set_autocommit(False)

        test = Test(
            module_part=initial['module_part'],
            name=data['name'],
            type=data['type'],
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
        return redirect(reverse_lazy('module_management:module_part_detail', kwargs={'pk': pk}))


class TestDeleteView(generic.DeleteView):
    model = Test
    template_name = 'module_management/test_delete.html'
    success_url = reverse_lazy('module_management:module_overview')

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.kwargs['pk']

        if Grade.objects.filter(test=pk):
            raise PermissionDenied('Cannot remove a test that has grades')

        if not Test.objects.filter(Q(pk=pk) & (Q(module_part__module_edition__coordinators__user=user))):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
