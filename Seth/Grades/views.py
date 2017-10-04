from collections import OrderedDict

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views import generic
from .models import Module, Studying, Person, Module_ed, Test, Course, Grade
import csv
import re
from django.utils.encoding import smart_str


class ModuleView(generic.ListView):
    template_name = 'Grades/modules.html'
    context_object_name = 'module_list'

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not Module_ed.objects.filter(Q(module_coordinator__user=user) | Q(courses__teachers__user=user)):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        module_set = Module_ed.objects.filter(Q(module_coordinator__user=user) | Q(courses__teachers__user=user))
        return set(module_set)


class GradeView(generic.DetailView):
    template_name = 'Grades/gradebook2.html'
    model = Module_ed

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not Module_ed.objects.filter(Q(module_coordinator__user=user) | Q(courses__teachers__user=user),
                                        id=self.kwargs['pk']):
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
        user = self.request.user
        context = super(GradeView, self).get_context_data(**kwargs)

        mod_ed = Module_ed.objects.prefetch_related('studying_set').get(id=self.kwargs['pk'])

        dicts = Studying.objects \
            .prefetch_related('student_id', 'study', 'student_id__Submitter') \
            .values('study__full_name', 'study__short_name', 'student_id', 'student_id__name', 'student_id__person_id',
                    'student_id__Submitter', 'student_id__Submitter__grade', 'student_id__Submitter__test_id',
                    'student_id__Submitter__released') \
            .filter(module_id=mod_ed) \
            .order_by('student_id__Submitter__test_id', 'student_id__Submitter__time')
        courses = Course.objects \
            .prefetch_related('test_set') \
            .filter(module_ed=mod_ed)
        tests = Test.objects \
            .filter(course_id__module_ed=mod_ed)

        students = dict()
        temp_dict = dict()
        context_dict = OrderedDict()

        for d in dicts:
            student = d['student_id']
            if student not in students.keys():
                students[student] = dict()
            if student not in temp_dict.keys():
                temp_dict[student] = dict()

            students[student]['name'] = d['student_id__name']
            students[student]['pid'] = d['student_id__person_id']
            students[student]['study'] = d['study__full_name']
            students[student]['sstudy'] = d['study__short_name']

            temp_dict[student][d['student_id__Submitter__test_id']] = (
            d['student_id__Submitter__grade'], d['student_id__Submitter__released'])

        for key in sorted(temp_dict):
            context_dict[key] = temp_dict[key]

        context['gradedict'] = context_dict
        context['studentdict'] = students
        context['courses'] = courses
        context['tests'] = tests

        return context

class StudentView(generic.DetailView):
    template_name = 'Grades/student.html'
    model = Person

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not Module_ed.objects.filter(user=user, id=self.kwargs['pk']):
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
        context = super(StudentView, self).get_context_data(**kwargs)
        grade_dict = dict()
        test_dict = dict()
        course_dict = dict()
        mod_width = dict()

        person = Person.objects.get(id=self.kwargs['pk'])

        for studying in Studying.objects.filter(student_id=person).prefetch_related('module_id'):
            course_list = []

            mod_ed = studying.module_id
            width = 0
            for course in mod_ed.courses.prefetch_related('test_set').all():
                test_list = []

                if course not in course_list:
                    course_list.append(course)

                for test in course.test_set.prefetch_related('grade_set').all():
                    gradelist = []

                    width += 1
                    if test not in test_list:
                        test_list.append(test)

                    for grade in test.grade_set.filter(student_id=person).filter(released=True):
                        gradelist.append(grade)

                    gradelist.sort(key=lambda gr: grade.time)
                    if gradelist == []:
                        course_list.pop(-1)
                    else:
                        grade_dict[test] = gradelist
                        test_dict[course] = test_list
            course_dict[mod_ed] = course_list
            mod_width[mod_ed] = width

        context['student'] = person
        context['gradedict'] = grade_dict
        context['testdict'] = test_dict
        context['coursedict'] = course_dict
        context['modwidth'] = mod_width

        return context


class ModuleStudentView(generic.DetailView):
    template_name = 'Grades/modulestudent.html'
    model = Module_ed

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not Module_ed.objects.filter(Q(module_coordinator__user=user) | Q(courses__teachers__user=user),
                                        id=self.kwargs['pk']):
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
        user = self.request.user
        context = super(ModuleStudentView, self).get_context_data(**kwargs)

        mod_ed = Module_ed.objects.prefetch_related('courses').get(id=self.kwargs['pk'])
        student = Person.objects.get(id=self.kwargs['sid'])

        dicts = Grade.objects \
            .prefetch_related('test_id') \
            .values('grade', 'released', 'test_id') \
            .filter(test_id__course_id__module_ed=mod_ed, student_id=student) \
            .order_by('test_id', 'time')
        courses = Course.objects \
            .prefetch_related('test_set') \
            .filter(module_ed=mod_ed)
        tests = Test.objects \
            .filter(course_id__module_ed=mod_ed)

        print(dicts)

        temp_dict = dict()
        context_dict = OrderedDict()

        for d in dicts:
            temp_dict[d['test_id']] = (d['grade'], d['released'])

        for key in sorted(temp_dict):
            context_dict[key] = temp_dict[key]

        context['student'] = student
        context['courses'] = courses
        context['tests'] = tests
        context['gradedict'] = context_dict

        return context


class CourseView(generic.DetailView):
    template_name = 'Grades/course.html'
    model = Course

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not Course.objects.filter(Q(module_ed__module_coordinator__user=user) | Q(teachers__user=user),
                                     id=self.kwargs['pk']):
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
        context = super(CourseView, self).get_context_data(**kwargs)

        test_dict = dict()
        test_all_released = dict()
        student_list = []
        study_dict = dict()
        role_dict = dict()

        course = Course.objects.get(id=self.kwargs['pk'])

        for mod_ed in Module_ed.objects.filter(courses=course).prefetch_related('studying_set'):
            for studying in mod_ed.studying_set.prefetch_related('student_id').all():
                if studying.student_id not in student_list:
                    student_list.append(studying.student_id)
                    study_dict[studying.student_id] = studying.study
                    role_dict[studying.student_id] = studying.role

        for test in Test.objects.filter(course_id=course).prefetch_related('grade_set'):

            grade_dict = dict()
            all_released = True

            for grade in test.grade_set.prefetch_related('student_id').all():
                if grade.student_id not in grade_dict.keys():
                    grade_dict[grade.student_id] = []
                grade_dict[grade.student_id].append(grade)

            for key in grade_dict.keys():
                grade_dict[key].sort(key=lambda gr: grade.time)
                if not grade_dict[key][-1].released:
                    all_released = False

            test_dict[test] = grade_dict
            test_all_released[test] = all_released

        context['course'] = course
        context['studentlist'] = student_list
        context['testdict'] = test_dict
        context['testallreleased'] = test_all_released
        context['studydict'] = study_dict
        context['roledict'] = role_dict
        context['module_ed'] = Module_ed.objects.filter(courses=course)[0]
        return context


class TestView(generic.DetailView):
    template_name = 'Grades/test.html'
    model = Test

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not Test.objects.filter(
                        Q(course_id__module_ed__module_coordinator__user=user) | Q(course_id__teachers__user=user),
                id=self.kwargs['pk']):
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
        context = super(TestView, self).get_context_data(**kwargs)

        if 'change' not in self.request.session.keys():
            context['change'] = False
        elif self.request.session['change'] == 1:
            context['change'] = 'The chosen grade(s) have successfully been released.'
        elif self.request.session['change'] == 2:
            context['change'] = 'The chosen grade(s) have successfully been retracted.'
        self.request.session['change'] = 0

        grade_dict = dict()
        student_list = []
        study_dict = dict()
        role_dict = dict()

        test = Test.objects.get(id=self.kwargs['pk'])

        for mod_ed in Module_ed.objects.filter(courses=test.course_id).prefetch_related('studying_set'):
            for studying in mod_ed.studying_set.prefetch_related('student_id').all():
                if studying.student_id not in student_list:
                    student_list.append(studying.student_id)
                    study_dict[studying.student_id] = studying.study
                    role_dict[studying.student_id] = studying.role

        for grade in test.grade_set.prefetch_related('student_id').all():
            if grade.student_id not in grade_dict.keys():
                grade_dict[grade.student_id] = [grade]
            else:
                grade_dict[grade.student_id].append(grade)
                grade_dict[grade.student_id].sort(key=lambda gr: grade.time)

        context['test'] = test
        context['studentlist'] = student_list
        context['gradedict'] = grade_dict
        context['studydict'] = study_dict
        context['roledict'] = role_dict
        context['module_ed'] = Module_ed.objects.filter(courses=test.course_id)[0]
        return context


def export(request, *args, **kwargs):
    user = request.user

    if not Module_ed.objects.filter(module_coordinator__user=user, id=kwargs['pk']):
        raise PermissionDenied()

    mod_ed = Module_ed.objects.prefetch_related('studying_set').prefetch_related('courses').get(id=kwargs['pk'])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + mod_ed.module.name + '.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    output = u'Student'
    for course in mod_ed.courses.prefetch_related('test_set').all():
        for test in course.test_set.all():
            output += ',' + test.name

    writer.writerow([
        smart_str(output),
    ])

    for studying in mod_ed.studying_set.prefetch_related('student_id'):

        output = u'' + studying.student_id.user.last_name + ' (' + studying.student_id.id_prefix + studying.student_id.person_id + ')'
        for course in mod_ed.courses.prefetch_related('test_set').all():
            for test in course.test_set.prefetch_related('grade_set').all():

                gradelist = []
                for grade in test.grade_set.filter(student_id=studying.student_id):
                    gradelist.append(grade)

                gradelist.sort(key=lambda gr: grade.time)
                if gradelist != []:
                    output += ',' + str(gradelist[-1].grade)
                else:
                    output += ',-'
        writer.writerow([
            smart_str(output)
        ])
    return response


def release(request, *args, **kwargs):
    user = request.user

    if not Module_ed.objects.filter(module_coordinator__user=user, id=kwargs['pk']):
        raise PermissionDenied()

    regex = re.compile("check[0-9]+")
    action = request.POST['action']

    for key in request.POST:
        key_search = re.search('check([0-9]+)', key)
        if key_search:
            grade_id = int(key_search.group(1))
            grade = Grade.objects.get(id=grade_id)

            if action == 'release':
                grade.released = True
                grade.save()
                request.session['change'] = 1
            elif action == 'retract':
                grade.released = False
                grade.save()
                request.session['change'] = 2

    # TODO: Send mail

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
