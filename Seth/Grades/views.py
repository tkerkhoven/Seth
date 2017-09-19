from django.shortcuts import render
from django.views import generic
from .models import Module, Studying, Person, Module_ed, Course, Test, Grade


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

        mod = Module_ed.objects.get(module=self.kwargs['pk'])
        for studying in Studying.objects.all().filter(module_id=mod.id):
            student_dict = dict()

            student_dict['id'] = studying.student_id.person_id
            student_dict['user'] = studying.student_id.user
            print(studying.student_id.user)
            for course in mod.courses.all():

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
    model = Module

    def get_context_data(self, **kwargs):
        context = super(StudentView, self).get_context_data(**kwargs)

        mod = Module_ed.objects.get(module=self.kwargs['pk'])
        student = Person.objects.get(person_id=self.kwargs['sid'])

        course_dict = dict()
        test_dict = dict()
        grade_dict = dict()

        for course in mod.courses.all():
            test_list = []

            if course.id not in course_dict.keys():
                course_dict[course.id] = course.name

            for test in Test.objects.all().filter(course_id=course):

                if test not in test_list:
                    test_list.append(test)

                for grade in Grade.objects.all().filter(student_id=student.person_id).filter(test_id=test):
                    grade_dict[test.id] = grade.grade

                test_dict[course.id] = test_list

        context['student'] = student
        context['user'] = student.user
        context['coursedict'] = course_dict
        context['testdict'] = test_dict
        context['gradedict'] = grade_dict
