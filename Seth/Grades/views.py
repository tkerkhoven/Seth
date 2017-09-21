from django.shortcuts import render
from django.views import generic
from .models import Module, Studying, Module_ed, Course, Test, Grade, Person
from django.urls import reverse_lazy
from .forms import UserUpdateForm



class ModuleView(generic.ListView):
    template_name = 'Grades/modules.html'
    model = Module

    def get_queryset(self):
        return Module.objects.order_by('name')


class GradeView(generic.DetailView):
    template_name = 'Grades/gradebook.html'
    model = Module

    def get_context_data(self, **kwargs):
        context = super(GradeView, self).get_context_data(**kwargs)

        dList = []
        tList = []
        courseDict = dict()
        testDict = dict()

        m_id = Module_ed.objects.get(module=self.kwargs['pk'])
        for studying in Studying.objects.all().filter(module_id=m_id):
            studentDict = dict()

            studentDict['id'] = studying.student_id
            studentDict['user'] = studying.student_id.user
            print(studying.student_id.user)
            for course in m_id.courses.all():

                tList = []
                if course.id not in courseDict.keys():
                    courseDict[course.id] = course.name

                for test in Test.objects.all().filter(course_id=course):

                    if test not in tList:
                        tList.append(test)

                    for grade in Grade.objects.all().filter(student_id=studying.student_id).filter(test_id=test):
                        studentDict[test.id] = grade.grade
                    testDict[course.id] = tList

            dList.append(studentDict)

        context['studentdict'] = dList
        context['coursedict'] = courseDict
        context['testdict'] = testDict
        return context


class StudentView(generic.DetailView):
    template_name = 'Grades/student.html'
    model = Course

    def get_context_data(self, **kwargs):
        context = super(StudentView, self).get_context_data(**kwargs)

        mod = Module_ed.objects.get(module=self.kwargs['pk'])
        stu = Student.objects.get(student_id=self.kwargs['sid'])

        tList = []
        courseDict = dict()
        testDict = dict()
        gradeDict = dict()

        for course in mod.courses.all():
            tList = []

            if course.id not in courseDict.keys():
                courseDict[course.id] = course.name

            for test in Test.objects.all().filer(course_id=course):

                if test not in tList:
                    tList.append(test)

                for grade in Grade.objects.all().filter(student_id=studying.student_id).filter(test_id=test):
                    gradeDict[test.id] = grade.grade

                testDict[course.id] = tList

        context['student'] = stu
        context['user'] = stu.user
        context['coursedict'] = courseDict
        context['testdict'] = testDict
        context['gradedict'] = gradeDict


class PersonsView(generic.ListView):
    template_name = 'Grades/users.html'
    model = Person

    def get_context_data(self, **kwargs):
        context = super(PersonsView, self).get_context_data(**kwargs)

        persons = Person.objects.all()
        person_dict = dict()
        for person in persons.all():
            data = dict()
            data['name'] = person.name
            data['role'] = person.role
            data['full_id'] = person.full_id
            person_dict[person.id] = data
            print(person.name)
        context['persons'] = person_dict
        return context


class PersonDetailView(generic.DetailView):
    template_name = 'Grades/user.html'
    model = Person

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)
        person = Person.objects.get(id=self.kwargs['pk'])
        data = dict()
        data['name'] = person.name
        data['id'] = person.id
        data['start'] = person.start
        data['stop'] = person.stop
        data['role'] = person.role
        data['studies'] = person.studies
        print(person.studies)
        data['full_id'] = person.full_id
        context['person'] = data
        return context


class UpdateUser(generic.UpdateView):
    model = Person
    # fields = ('name', 'start', 'stop', 'role', 'studies')
    template_name_suffix = '/update-user'
    form_class = UserUpdateForm

    # success_url = reverse_lazy('grades:user', args=(!!self.object.id!!))

    # def get_context_data(self):
    #     context = super(PersonDetailView, self).get_context_data(**kwargs)
    #     person = Person.objects.get(id=self.kwargs['pk'])
    #
    #     data = dict()
    #     data['id'] = person.id
    #     context['person'] = data

    def get_success_url(self):
        return reverse_lazy('grades:user', args=(self.object.id,))

    def get_absolute_url(self):
        return u'/grades/user/%d' % self.id

    def get_initial(self):
        initial = super(UpdateUser, self).get_initial()

        person = Person.objects.get(id=self.object.id)
        data = {
            'name': person.name,
            'id_prefix': person.id_prefix,
            'person_id': person.person_id,
            'start': person.start,
            'stop': person.stop,
            'role': person.role,
            'studies': person.studies
        }
        # initial['name'] = person.name
        return initial

        # def get_object(self, queryset=None):
        #     obj = Person.objects.get(id=self.kwargs['pk'])
        #     return obj
