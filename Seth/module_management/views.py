import pprint

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from django.forms.models import ModelForm
from django.forms.models import modelform_factory
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import ModelFormMixin
from django_select2.forms import Select2MultipleWidget

from Grades.models import Module, ModuleEdition, ModulePart, Test, Person, Coordinator, Teacher, Grade, Studying, Study


class ModuleListView(generic.ListView):
    template_name = 'module_management/module_overview.html'
    context_object_name = 'module_list'

    def get_queryset(self):
        user = self.request.user
        module_list = Module.objects.prefetch_related('moduleedition_set').filter(
            moduleedition__coordinators__user=user).distinct()
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
        context['studies'] = Study.objects.filter(modules__moduleedition__in=context['module_editions']).distinct()
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

        studying = Studying.objects.filter(module_edition=pk).prefetch_related('person').order_by('person__university_number')
        context['studying'] = studying

        module_parts = ModulePart.objects.filter(module_edition=pk)
        context['module_parts'] = module_parts

        coordinators = Coordinator.objects.filter(module_edition=pk).prefetch_related('person').order_by('person__university_number')
        context['coordinators'] = coordinators

        studies = Study.objects.filter(modules__moduleedition=pk)
        context['studies'] = studies
        return context


class ModuleEditionUpdateView(generic.UpdateView):
    template_name = 'module_management/module_edition_update.html'
    model = ModuleEdition
    fields = ['year', 'block']

    def get_context_data(self, **kwargs):
        context = super(ModuleEditionUpdateView, self).get_context_data(**kwargs)
        context['module_edition_override'] = str(ModuleEdition.objects.get(pk=self.kwargs['pk']))
        return context

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = request.user

        if not ModuleEdition.objects.filter(coordinators__user=user).filter(pk=pk):
            raise PermissionDenied()

        return super(ModuleEditionUpdateView, self).dispatch(request, *args, **kwargs)


class ModuleEditionCreateForm(ModelForm):
    class Meta:
        model = ModuleEdition
        fields = ['module', 'year', 'block', 'coordinators']

    def __init__(self, *args, **kwargs):
        super(ModuleEditionCreateForm, self).__init__(*args, **kwargs)
        self.fields['module'].widget.attrs['disabled'] = True
        self.fields['coordinators'].widget.attrs['disabled'] = True
        self.fields['coordinators'].queryset = kwargs['initial']['coordinators']


class ModuleEditionCreateView(generic.CreateView):
    template_name = 'module_management/module_edition_create.html'
    form_class = ModuleEditionCreateForm

    def get_initial(self):
        pk = self.kwargs['pk']
        latest_module_edition = ModuleEdition.objects.filter(module=pk).order_by('-year', '-block')[0].pk
        return {
            'module': Module.objects.get(pk=pk),
            'coordinators': Person.objects.filter(coordinator__module_edition=latest_module_edition)
        }

    def get_context_data(self, **kwargs):
        context = super(ModuleEditionCreateView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']

        mod = Module.objects.get(pk=pk)
        context['module'] = mod

        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.kwargs['pk']
        latest_module_edition = ModuleEdition.objects.filter(module=pk).order_by('-year', '-block')[0].pk

        if not Person.objects.filter(coordinator__module_edition=latest_module_edition).filter(user=user):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        initial = self.get_form_kwargs()['initial']
        data = self.get_form_kwargs()['data']
        pk = self.kwargs['pk']
        latest_module_edition = ModuleEdition.objects.filter(module=pk).order_by('-year', '-block')[0].pk

        module_edition = ModuleEdition(
            module=initial['module'],
            year=data['year'],
            block=data['block']
        )

        try:
            module_edition.full_clean()
        except ValidationError as e:
            pp = pprint.PrettyPrinter(indent=4, width=120)
            return HttpResponseBadRequest(pp.pformat(('Form data is invalid: ', e.message_dict)))
        module_edition.save()

        old_module_parts = ModulePart.objects.filter(module_edition=latest_module_edition).prefetch_related('test_set')
        new_module_parts = []
        for old_module_part in old_module_parts:
            module_part = ModulePart(
                module_edition=module_edition,
                name=old_module_part.name
            )
            try:
                module_part.full_clean()
            except ValidationError as e:
                pp = pprint.PrettyPrinter(indent=4, width=120)
                return HttpResponseBadRequest(pp.pformat(('Module Part is invalid: ', e.message_dict)))
            new_module_parts.append(module_part)
        ModulePart.objects.bulk_create(new_module_parts)

        new_tests = []
        for i in range(len(old_module_parts)):
            old_tests = old_module_parts[i].test_set.all()  # Test.objects.filter(module_part=old_module_parts[i].pk).distinct()
            for old_test in old_tests:
                test = Test(
                    maximum_grade=old_test.maximum_grade,
                    minimum_grade=old_test.minimum_grade,
                    module_part=new_module_parts[i],
                    name=old_test.name,
                    released=False,
                    type=old_test.type
                )
                try:
                    test.full_clean()
                except ValidationError as e:
                    pp = pprint.PrettyPrinter(indent=4, width=120)
                    return HttpResponseBadRequest(pp.pformat(('Test is invalid: ', e.message_dict)))
                new_tests.append(test)
        Test.objects.bulk_create(new_tests)

        new_coordinators = []
        old_persons = Person.objects.filter(id__in=initial['coordinators']).prefetch_related('coordinator_set')
        for person in old_persons:
            coordinator = Coordinator(
                module_edition=module_edition,
                person=person,
                # is_assistant=Coordinator.objects.get(person=person, module_edition=latest_module_edition).is_assistant
                is_assistant=person.coordinator_set.get(module_edition=latest_module_edition).is_assistant
            )
            try:
                coordinator.full_clean()
            except ValidationError as e:
                pp = pprint.PrettyPrinter(indent=4, width=120)
                return HttpResponseBadRequest(pp.pformat(('Coordinator is invalid: ', e.message_dict)))
            new_coordinators.append(coordinator)
        Coordinator.objects.bulk_create(new_coordinators)

        return redirect('module_management:module_overview')


class ModulePartDetailView(generic.DetailView):
    template_name = 'module_management/module_part_detail.html'
    model = ModulePart

    def get_context_data(self, **kwargs):
        context = super(ModulePartDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']

        module_edition = ModuleEdition.objects.get(modulepart=pk)
        studying = Studying.objects.filter(module_edition=module_edition).prefetch_related('person').order_by('person__university_number')
        context['studying'] = studying
        teachers = Teacher.objects.filter(module_part=pk).prefetch_related('person').order_by('person__university_number')
        context['teachers'] = teachers

        return context

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = request.user

        if not ModulePart.objects.filter(Q(pk=pk) & Q(module_edition__coordinators__user=user)):
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
    form_class = modelform_factory(ModulePart, fields=['name', 'teachers'], widgets={'teachers': Select2MultipleWidget})

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
            if t.university_number[0] == 'm':
                teacher.role = 'T'
            else:
                teacher.role = 'A'
            teacher.save()
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)


class ModulePartCreateView(generic.CreateView):
    template_name = 'module_management/module_part_create.html'
    form_class = modelform_factory(ModulePart, fields=['name', 'teachers'], widgets={'teachers': Select2MultipleWidget})

    def get_context_data(self, **kwargs):
        context = super(ModulePartCreateView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']

        module_edition = ModuleEdition.objects.get(pk=pk)
        context['module_edition'] = module_edition

        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk = self.kwargs['pk']

        if not Person.objects.filter(coordinator__module_edition=pk).filter(user=user):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = self.get_form_kwargs()['data']
        pk = self.kwargs['pk']

        module_part = ModulePart(
            name=data['name'],
            module_edition=ModuleEdition.objects.get(pk=pk)
        )
        try:
            module_part.full_clean()
        except ValidationError as e:
            pp = pprint.PrettyPrinter(indent=4, width=120)
            return HttpResponseBadRequest(pp.pformat(('Form data is invalid: ', e.message_dict)))
        module_part.save()

        for t in data.getlist('teachers'):
            t = Person.objects.get(pk=t)
            if t.university_number[0] == 'm':
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
                return HttpResponseBadRequest(pp.pformat(('Teacher is invalid: ', e.message_dict)))
            teacher.save()

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
        if not Test.objects.filter(Q(pk=pk) & Q(module_part__module_edition__coordinators__user=user)):
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
    fields = ['name', 'type', 'maximum_grade', 'minimum_grade']

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = request.user
        if not Test.objects.filter(Q(pk=pk) & Q(module_part__module_edition__coordinators__user=user)):
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
        fields = ['module_part', 'name', 'type', 'maximum_grade', 'minimum_grade']

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

    def get_context_data(self, **kwargs):
        context = super(TestCreateView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']

        module_part = ModulePart.objects.get(pk=pk)
        context['module_part'] = module_part

        return context

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

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        initial = self.get_form_kwargs()['initial']
        data = self.get_form_kwargs()['data']
        pk = self.kwargs['pk']

        test = Test(
            module_part=initial['module_part'],
            name=data['name'],
            type=data['type'],
            maximum_grade=data['maximum_grade'],
            minimum_grade=data['minimum_grade']
        )
        try:
            test.full_clean()
        except ValidationError as e:
            pp = pprint.PrettyPrinter(indent=4, width=120)
            return HttpResponseBadRequest(pp.pformat(('Form data is invalid: ', e.message_dict)))
        test.save()

        return redirect(reverse_lazy('module_management:test_detail', kwargs={'pk': test.pk}))


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


@transaction.atomic
def remove_user(request, spk, mpk):
    # Authentication
    user = request.user
    if not ModuleEdition.objects.filter(pk=mpk, coordinators__user=user):
        raise PermissionDenied("Something went wrong")

    person = Person.objects.get(id=spk)
    module_ed = ModuleEdition.objects.get(id=mpk)
    grades = Grade.objects.filter(test__module_part__module_edition=mpk).filter(student=person)
    studying = Studying.objects.get(person=person, module_edition=module_ed)
    context = dict()
    context['person_name'] = person.name
    context['person_number'] = person.university_number
    context['person_pk'] = person.pk
    context['module_code'] = module_ed.code
    context['module_name'] = module_ed.module.name
    if len(grades) == 0:
        studying.delete()
        context['success'] = True
    else:
        context['success'] = False
    # return render(request, 'module_management/user_delete.html', context=context)
    return JsonResponse(context)
