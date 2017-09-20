from django.views import generic
from .models import Module, Studying, Person, Module_ed, Test, Course, Grade
from django.contrib.auth.models import User


class ModuleView(generic.ListView):
    template_name = 'Grades/modules.html'
    context_object_name = 'module_list'

    def get_queryset(self):
        module_set = Module.objects.prefetch_related('module_ed_set')
        return module_set


class GradeView(generic.DetailView):
    template_name = 'Grades/gradebook.html'
    model = Module

    def get_context_data(self, **kwargs):
        context = super(GradeView, self).get_context_data(**kwargs)

        student_list = []
        course_dict = dict()
        test_dict = dict()

        mod_ed = Module_ed.objects.prefetch_related('studying_set').prefetch_related('courses').get(
            module=self.kwargs['pk'])
        for studying in mod_ed.studying_set.prefetch_related('student_id'):
            student_dict = dict()

            student_dict['user'] = studying.student_id.user
            for course in mod_ed.courses.prefetch_related('test_set').all():
                test_list = []
                if course not in course_dict.keys():
                    course_dict[course] = course.name

                for test in course.test_set.prefetch_related('grade_set').all():

                    if test not in test_list:
                        test_list.append(test)

                    for grade in test.grade_set.filter(student_id=studying.student_id):
                        student_dict[test] = grade.grade
                    test_dict[course] = test_list

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

        for studying in Studying.objects.filter(student_id=person).prefetch_related('module_id'):
            course_list = []

            mod_ed = studying.module_id
            for course in mod_ed.courses.prefetch_related('test_set').all():
                test_list = []

                if course not in course_list:
                    course_list.append(course)

                for test in course.test_set.prefetch_related('grade_set').all():

                    if test not in test_list:
                        test_list.append(test)

                    for grade in test.grade_set.filter(student_id=person):
                        grade_dict[test] = grade.grade

                test_dict[course] = test_list
            course_dict[mod_ed] = course_list

        context['student'] = person
        context['gradedict'] = grade_dict
        context['testdict'] = test_dict
        context['coursedict'] = course_dict

        return context


class ModuleStudentView(generic.DetailView):
    template_name = 'Grades/modulestudent.html'
    model = Module

    def get_context_data(self, **kwargs):
        context = super(ModuleStudentView, self).get_context_data(**kwargs)

        mod_ed = Module_ed.objects.prefetch_related('courses').get(module=self.kwargs['pk'])
        student = Person.objects.prefetch_related('user').get(user=self.kwargs['sid'])

        course_list = []
        test_dict = dict()
        grade_dict = dict()

        for course in mod_ed.courses.prefetch_related('test_set').all():
            test_list = []

            if course not in course_list:
                course_list.append(course)

            for test in course.test_set.prefetch_related('grade_set').all():

                if test not in test_list:
                    test_list.append(test)

                for grade in test.grade_set.filter(student_id=student):
                    grade_dict[test] = grade.grade

                test_dict[course] = test_list

        context['student'] = student
        context['courselist'] = course_list
        context['testdict'] = test_dict
        context['gradedict'] = grade_dict

        return context


class CourseView(generic.DetailView):
    template_name = 'Grades/course.html'
    model = Course

    def get_context_data(self, **kwargs):
        context = super(CourseView, self).get_context_data(**kwargs)

        test_dict = dict()
        student_list = []

        course = Course.objects.get(id=self.kwargs['pk'])

        for mod_ed in Module_ed.objects.filter(courses=course).prefetch_related('studying_set'):
            for studying in mod_ed.studying_set.prefetch_related('student_id').all():
                if studying.student_id not in student_list:
                    student_list.append(studying.student_id)

        for test in Test.objects.filter(course_id=course).prefetch_related('grade_set'):

            grade_dict = dict()
            for grade in test.grade_set.prefetch_related('student_id').all():
                grade_dict[grade.student_id] = grade.grade
            test_dict[test] = grade_dict

        context['course'] = course
        context['studentlist'] = student_list
        context['testdict'] = test_dict
        return context


class TestView(generic.DetailView):
    template_name = 'Grades/test.html'
    model = Test

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)

        grade_dict = dict()
        student_list = []

        test = Test.objects.get(id=self.kwargs['pk'])

        for mod_ed in Module_ed.objects.filter(courses=test.course_id).prefetch_related('studying_set'):
            for studying in mod_ed.studying_set.prefetch_related('student_id').all():
                if studying.student_id not in student_list:
                    student_list.append(studying.student_id)

        for grade in test.grade_set.prefetch_related('student_id').all():
            grade_dict[grade.student_id] = grade.grade

        context['test'] = test
        context['studentlist'] = student_list
        context['gradedict'] = grade_dict
        return context
