from django.shortcuts import render
from django.contrib.auth.models import User
from Grades.models import Person, ModuleEdition, Studying, ModulePart, Study, Module, Teacher, Coordinator
from django.views import generic
from django.urls import reverse_lazy
from .forms import UserUpdateForm, CreateUserForm
from django.core.exceptions import PermissionDenied
from django.db.models import prefetch_related_objects
from django.db.models.query import EmptyQuerySet
from django.shortcuts import redirect

import permission_utils as pu


def known_persons(person):
    """
    Returns all Person-objects that are considered to be related to a given user.
    Case Coordinator/Coordinator-assistant: Return all students from all modules that are coordinated by that person
    Case Teacher: Return all students from moduleparts that are taught by that person
    Case Adviser: Return all students that are in all modules of all studies that have that person as adviser
    Users can be part of multiple cases.

    :param person: The person all other persons must be related to.
    :return: All persons related to the given user.
    """
    queryset = Person.objects.none()
    if pu.is_coordinator_or_assistant(person):
        # Add Students
        module_eds = ModuleEdition.objects.all().filter(coordinators=person).prefetch_related()
        studyings = Studying.objects.all().filter(module_edition__in=module_eds).prefetch_related()
        students = Person.objects.all().filter(studying__in=studyings).distinct()
        queryset = queryset.union(queryset, students)
        # Add Study Advisers
        modules = Module.objects.filter(moduleedition__in=module_eds)
        studies = Study.objects.none()
        for mod in modules:
            study_set = Study.objects.filter(modules=mod)
            studies = (studies.all() | study_set.all())
        advisers = Person.objects.filter(study__in=studies)
        queryset = queryset.union(queryset, advisers)
        # Add Teachers and Teaching Assistants
        module_parts = ModulePart.objects.all().filter(module_edition__in=module_eds)
        teachers_obj = Teacher.objects.filter(module_part__in=module_parts)
        teachers = Person.objects.filter(teacher__in=teachers_obj)
        queryset = queryset.union(queryset, teachers)
        # Add other coordinators
        coordinator_obj = Coordinator.objects.filter(module_edition__in=module_eds)
        coordinators = Person.objects.filter(coordinator__in=coordinator_obj)
        queryset = queryset.union(queryset, coordinators)

    if pu.is_teacher(person):
        # Add Students and teaching assistants
        module_parts = ModulePart.objects.filter(teacher__person=person).prefetch_related()
        module_eds = ModuleEdition.objects.filter(modulepart__in=module_parts).prefetch_related()
        studyings = Studying.objects.all().filter(module_edition__in=module_eds).prefetch_related()
        persons = Person.objects.all().filter(studying__in=studyings).distinct()
        queryset = queryset.union(queryset, persons)
        # Add Teachers
        known_module_parts = ModulePart.objects.filter(module_edition__in=module_eds)
        teachers_obj = Teacher.objects.filter(module_part__in=known_module_parts)
        teachers = Person.objects.filter(teacher__in=teachers_obj)
        queryset = queryset.union(queryset, teachers)
        # Add Module Coordinators
        coordinator_obj = Coordinator.objects.filter(module_edition__in=module_eds)
        coordinators = Person.objects.filter(coordinator__in=coordinator_obj)
        queryset = queryset.union(queryset, coordinators)
        # Add Advisers
        modules = Module.objects.filter(moduleedition__in=module_eds)
        studies = Study.objects.none()
        for mod in modules:
            study_set = Study.objects.filter(modules=mod)
            studies.union(study_set)
        advisers = Person.objects.filter(study__in=studies)
        queryset = queryset.union(queryset, advisers)

    if pu.is_study_adviser(person):
        # Add students
        studies = Study.objects.filter(advisers=person).prefetch_related()
        modules = Module.objects.filter(study__in=studies).prefetch_related()
        module_eds = ModuleEdition.objects.filter(module__in=modules).prefetch_related()
        studyings = Studying.objects.all().filter(module_edition__in=module_eds).prefetch_related()
        persons = Person.objects.all().filter(studying__in=studyings).distinct()
        queryset = queryset.union(queryset, persons)
        # Add coordinators
        coordinator_obj = Coordinator.objects.filter(module_edition__in=module_eds)
        coordinators = Person.objects.filter(coordinator__in=coordinator_obj)
        queryset = queryset.union(queryset, coordinators)
        # queryset = (queryset | coordinators)
        # Add teachers
        module_parts = ModulePart.objects.filter(module_edition__in=module_eds)
        teacher_obj = Teacher.objects.filter(module_part__in=module_parts)
        teachers = Person.objects.filter(teacher__in=teacher_obj)
        queryset = queryset.union(queryset, teachers)
        # Add advisers
        advisers = Person.objects.filter(study__in=studies)
        queryset = queryset.union(queryset, advisers)
    result = queryset.distinct()
    return result


# Create your views here.
class PersonsView(generic.ListView):
    """
    Gives a generic.ListView of all relevant Persons to the logged in user.
    """
    template_name = 'human_resource/users.html'
    model = Person
    person = None

    def dispatch(self, request, *args, **kwargs):
        self.person = Person.objects.filter(user=request.user).first()
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
    """
    Gives a generic.DetailView of a specific Person relevant to the logged in user.
    """
    template_name = 'human_resource/user.html'
    model = Person

    def dispatch(self, request, *args, **kwargs):
        user = Person.objects.filter(user=request.user).first()
        person = Person.objects.get(id=self.kwargs['pk'])
        if person in known_persons(user):
            return super(PersonDetailView, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to access the details of this user')

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)
        person = Person.objects.filter(id=self.kwargs['pk']).first()
        data = dict()
        context['person'] = person
        context['studies'] = Studying.objects.filter(person=person)
        return context


class UpdatePerson(generic.UpdateView):
    """
    Gives a generic.UpdateView of a specific Person relevant to the logged in user.
    """
    model = Person
    template_name = 'human_resource/person/update-user.html'
    # template_name_suffix = '/update-user'
    form_class = UserUpdateForm

    def dispatch(self, request, *args, **kwargs):
        user = Person.objects.filter(user=request.user).first()
        person = Person.objects.filter(id=self.kwargs['pk']).first()
        if person in known_persons(user):
            return super(UpdatePerson, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to access the details of this user')

    def get_success_url(self):
        return reverse_lazy('human_resource:user', args=(self.object.id,))

    def get_absolute_url(self):
        return u'/human_resource/user/%d' % self.id

    def get_initial(self):
        initial = super(UpdatePerson, self).get_initial()
        return initial

        # def get_object(self, queryset=None):
        #     obj = Person.objects.get(id=self.kwargs['pk'])
        #     return obj


class DeletePerson(generic.DeleteView):
    """
    Gives a generic.Deleteview of a specific Person relevant to the logged in user.
    """
    model = Person
    template_name = 'human_resource/person_confirm_delete.html'
    success_url = reverse_lazy('human_resource:users')

    def dispatch(self, request, *args, **kwargs):
        user = Person.objects.filter(user=request.user).first()
        person = Person.objects.filter(id=self.kwargs['pk']).first()
        if person in known_persons(user):
            return super(DeletePerson, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to delete this user.')


class CreatePerson(generic.CreateView):
    model = Person
    template_name = 'human_resource/person_form.html'
    fields = '__all__'

    def dispatch(self, request, *args, **kwargs):
        person = Person.objects.filter(user=request.user).first()
        if pu.is_coordinator(person):
            return super(CreatePerson, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to create a user.')

    def get_success_url(self):
        return reverse_lazy('human_resource:user', args=(self.object.id,))


class CreatePersonNew(generic.FormView):
    template_name = 'human_resource/person_form.html'
    success_url = reverse_lazy('human_resource:users')
    form_class = CreateUserForm

    def dispatch(self, request, *args, **kwargs):
        person = Person.objects.filter(user=request.user).first()
        if pu.is_coordinator(person):
            return super(CreatePersonNew, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to create a user.')

    def form_valid(self, form):
        person_name = form.cleaned_data['name']
        ut_number = form.cleaned_data['university_number']
        email = form.cleaned_data['email_address']
        person_user = form.cleaned_data['user']
        if form.cleaned_data['create_teacher']:
            role = form.cleaned_data['role_teacher']
            module_part = form.cleaned_data['module_part_teacher']
            # todo Nieuwe user aanmaken met als username het medewerkersnummer
            person = Person.objects.get_or_create(name=person_name, university_number=ut_number, email=email, user=person_user)[0]
            Teacher.objects.get_or_create(person=person, module_part=module_part, role=role)
        else:
            person = Person.objects.get_or_create(name=person_name, university_number=ut_number, email=email, user=person_user)
            print("Don't create teacher")
        return super(CreatePersonNew, self).form_valid(form)
