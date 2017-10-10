from django.shortcuts import render
from Grades.models import Person
from django.views import generic
from django.urls import reverse_lazy
from .forms import UserUpdateForm, CreateUserForm

# Create your views here.
class PersonsView(generic.ListView):
    template_name = 'human_resource/users.html'
    model = Person

    def get_context_data(self, **kwargs):
        context = super(PersonsView, self).get_context_data(**kwargs)
        persons = Person.objects.all().order_by('name')
        context['persons'] = persons
        return context


class PersonDetailView(generic.DetailView):
    template_name = 'human_resource/user.html'
    model = Person

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


class CreatePerson(generic.CreateView):
    model = Person
    template_name = 'human_resource/person_form.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('human_resource:user', args=(self.object.id,))


class CreatePersonNew(generic.FormView):
    template_name = 'human_resource/person_form.html'
    form_class = CreateUserForm

    def form_invalid(self, form):
        print("Wrong")

    def form_valid(self, form):
        if form.cleaned_data['create_teacher']:
            print("Create teacher")
        else:
            print("Don't create teacher")
        print("right")

