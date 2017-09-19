from django.views import generic
from .models import Module, Studying, Person, Module_ed, Test, Grade
from django.contrib.auth.models import User


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

        student_list = []
        course_dict = dict()
        test_dict = dict()

        mod_ed = Module_ed.objects.get(module=self.kwargs['pk'])
        for studying in Studying.objects.all().filter(module_id=mod_ed.id):
            student_dict = dict()

            student_dict['id'] = studying.student_id.user.id
            student_dict['user'] = studying.student_id.user
            for course in mod_ed.courses.all():

                test_list = []
                if course.id not in course_dict.keys():
                    course_dict[course.id] = course.name

                for test in Test.objects.all().filter(course_id=course):

                    if test not in test_list:
                        test_list.append(test)

                    for grade in Grade.objects.all().filter(student_id=studying.student_id).filter(test_id=test):
                        student_dict[test.id] = grade.grade
                    test_dict[course.id] = test_list

            student_list.append(student_dict)

        context['studentdict'] = student_list
        context['coursedict'] = course_dict
        context['testdict'] = test_dict
        return context

class StudentView(generic.DetailView):
    template_name = 'Grades/student.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super(StudentView, self).get_context_data(**kwargs)

        grade_dict = dict()
        test_dict = dict()
        course_dict = dict()

        person = Person.objects.get(user=self.kwargs['pk'])
        for grade in Grade.objects.all().filter(student_id=person):
            if grade.test_id.course_id not in test_dict.keys():
                test_dict[grade.test_id.course_id] = []

            grade_dict[grade.test_id] = grade.grade
            test_dict[grade.test_id.course_id].append(grade.test_id)
            course_dict[grade.test_id.course_id] = grade.test_id.course_id.name

        context['student'] = True
        context['gradedict'] = grade_dict
        context['testdict'] = test_dict
        context['coursedict'] = course_dict

        return context

class ModuleStudentView(generic.DetailView):
    template_name = 'Grades/student.html'
    model = Module

    def get_context_data(self, **kwargs):
        context = super(ModuleStudentView, self).get_context_data(**kwargs)

        mod_ed = Module_ed.objects.get(module=self.kwargs['pk'])
        student = Person.objects.get(person_id=self.kwargs['sid'])

        course_dict = dict()
        test_dict = dict()
        grade_dict = dict()

        for course in mod_ed.courses.all():
            test_list = []

            if course.id not in course_dict.keys():
                course_dict[course.id] = course.name

            for test in Test.objects.all().filter(course_id=course):

                if test not in test_list:
                    test_list.append(test)

                print(test)
                for grade in Grade.objects.all().filter(student_id=student.person_id).filter(test_id=test):
                    grade_dict[test.id] = grade.grade

                test_dict[course.id] = test_list

        context['module_student'] = True
        context['student'] = student
        context['user'] = student.user
        context['coursedict'] = course_dict
        context['testdict'] = test_dict
        context['gradedict'] = grade_dict

        return context
