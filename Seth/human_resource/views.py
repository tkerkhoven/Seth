from django.shortcuts import render
from Grades.models import Person
from django.views import generic
from django.urls import reverse_lazy
from .forms import UserUpdateForm

# Create your views here.
class PersonsView(generic.ListView):
    template_name = 'human_resource/users.html'
    model = Person

    def get_context_data(self, **kwargs):
        context = super(PersonsView, self).get_context_data(**kwargs)

        persons = Person.objects.all()
        person_dict = dict()
        for person in persons.all():
            data = dict()
            data['name'] = person.name
            data['full_id'] = person.full_id
            person_dict[person.id] = data
            print(person.name)
        context['persons'] = person_dict
        return context


class PersonDetailView(generic.DetailView):
    template_name = 'human_resource/user.html'
    model = Person

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)
        person = Person.objects.get(id=self.kwargs['pk'])
        data = dict()
        data['name'] = person.name
        data['id'] = person.id
        data['start'] = person.start
        data['end'] = person.end
        data['full_id'] = person.full_id
        data['email'] = person.email
        data['studying_set'] = person.studying_set.all()
        context['person'] = data
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
