from django.shortcuts import render
from Grades.models import Person, ModuleEdition, Studying, ModulePart, Study, Module
from django.views import generic
from django.urls import reverse_lazy
from .forms import UserUpdateForm
from django.core.exceptions import PermissionDenied

import permission_utils as pu


def known_persons(person):
    result = []
    if pu.is_coordinator_or_assistant(person):
        modules = ModuleEdition.objects.all().filter(coordinators=person).prefetch_related()
        studyings = Studying.objects.all().filter(module_edition__in=modules).prefetch_related()
        persons = Person.objects.all().filter(studying__in=studyings).distinct()
        result.extend(persons)
        # Todo: Add study adviser, teachers, teaching assistants and other coordinators
    if pu.is_teacher(person):
        module_parts = ModulePart.objects.filter(teacher=person).prefetch_related()
        modules = ModuleEdition.objects.filter(module_edition__in=module_parts).prefetch_related()
        studyings = Studying.objects.all().filter(module_edition__in=modules).prefetch_related()
        persons = Person.objects.all().filter(studying__in=studyings).distinct()
        result.extend(persons)
        # Todo: add other teachers, teaching assistants and module coordinators (and advisers?)
    if pu.is_study_adviser(person):
        studies = Study.objects.filter(adviser=person).prefetch_related()
        modules = Module.objects.filter(module__in=studies).prefetch_related()
        module_eds = ModuleEdition.filter(module__in=modules).prefetch.related()
        studyings = Studying.objects.all().filter(module_edition__in=module_eds).prefetch_related()
        persons = Person.objects.all().filter(studying__in=studyings).distinct()
        result.extend(persons)
        # Todo: add coordinators, teachers, teaching assistants and other advisers

    return result


# Create your views here.
class PersonsView(generic.ListView):
    template_name = 'human_resource/users.html'
    model = Person
    person = None

    def dispatch(self, request, *args, **kwargs):
        self.person = Person.objects.filter(user=request.user)
        if pu.is_coordinator_or_assistant(self.person) or pu.is_teacher(self.person) or pu.is_study_adviser(
                self.person):
            return super(PersonsView, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not a module coordinator')

    def get_context_data(self, **kwargs):
        context = super(PersonsView, self).get_context_data(**kwargs)
        context['persons'] = known_persons(self.person)
        return context


class PersonDetailView(generic.DetailView):
    template_name = 'human_resource/user.html'
    model = Person

    def dispatch(self, request, *args, **kwargs):
        user = Person.objects.filter(user=request.user)
        person = Person.objects.get(id=self.kwargs['pk'])
        if person in known_persons(user):
            return super(PersonDetailView, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to access the details of this user')

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)
        person = Person.objects.get(id=self.kwargs['pk'])
        data = dict()
        context['person'] = person
        if person.studying_set.values('study'):
            context['studies'] = person.studying_set.values('study')[0].values
        return context


class UpdateUser(generic.UpdateView):
    model = Person
    template_name = 'human_resource/person/update-user.html'
    # template_name_suffix = '/update-user'
    form_class = UserUpdateForm

    def dispatch(self, request, *args, **kwargs):
        user = Person.objects.filter(user=request.user)
        person = Person.objects.get(id=self.kwargs['pk'])
        if person in known_persons(user):
            return super(UpdateUser, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to access the details of this user')

    def get_success_url(self):
        return reverse_lazy('human_resource:user', args=(self.object.id,))

    def get_absolute_url(self):
        return u'/human_resource/user/%d' % self.id

    def get_initial(self):
        initial = super(UpdateUser, self).get_initial()
        return initial

        # def get_object(self, queryset=None):
        #     obj = Person.objects.get(id=self.kwargs['pk'])
        #     return obj


class DeleteUser(generic.DeleteView):
    model = Person
    template_name = 'human_resource/person_confirm_delete.html'
    success_url = reverse_lazy('human_resource:users')

    def dispatch(self, request, *args, **kwargs):
        user = Person.objects.filter(user=request.user)
        person = Person.objects.get(id=self.kwargs['pk'])
        if person in known_persons(user):
            return super(PersonDetailView, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to access the details of this user')


class CreatePerson(generic.CreateView):
    model = Person
    template_name = 'human_resource/person_form.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('human_resource:user', args=(self.object.id,))
