from collections import OrderedDict
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views import generic
import django_excel as excel
from Grades.mailing import make_mail_grade_released, make_mail_grade_retracted
from .models import Studying, Person, ModuleEdition, Test, ModulePart, Grade, Module
import re


class ModuleView(generic.ListView):
    """ Module view of the grades module.

    Module coordinator and teachers are presented with a list of modules they have access to.
    Module coordinators have access to all modules they are a coordinator of, as well as all modules they are a teacher in.

    Teachers are presented with all modules they are a teacher in.
    """
    template_name = 'Grades/modules.html'
    context_object_name = 'module_list'

    # Check if the user is a module coordinator or a teacher.
    # If not, show them an error page.
    # If they are a student, this redirects them to their specific grade page.
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Redirect students
        studying = Studying.objects.filter(person__user=request.user)
        if studying:
            return redirect('grades:student', studying[0].person.id)

        # Check if the user is a module coordinator or a teacher
        if not ModuleEdition.objects.filter(Q(coordinators__user=user) | (Q(modulepart__teachers__user=user) & Q(modulepart__teacher__role='T'))):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    # Get the queryset for the specified user.
    def get_queryset(self):
        user = self.request.user
        module_set = ModuleEdition.objects.filter(Q(coordinators__user=user) | (Q(modulepart__teachers__user=user) & Q(modulepart__teacher__role='T')))
        return set(module_set)


class GradeView(generic.DetailView):
    """ The main gradebook view for Module Coordinators and Teachers.
    This view will show the overview of students, module parts, tests and grades of a certain module.
    Module coordinators will see every module part and its information, while teachers will only see their respective module parts.
    """
    template_name = 'Grades/gradebook.html'
    model = ModuleEdition

    # Check if the user is a module coordinator or a teacher.
    # If not, show them an error page.
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is a module coordinator or a teacher
        if not ModuleEdition.objects.filter(Q(coordinators__user=user) | (Q(modulepart__teachers__user=user) & Q(modulepart__teacher__role='T')),
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

    # Sets the context data to be used in the template.
    def get_context_data(self, **kwargs):
        context = super(GradeView, self).get_context_data(**kwargs)

        # Get the specific module edition
        mod_ed = ModuleEdition.objects.get(id=self.kwargs['pk'])

        # Gather all module parts the user is allowed to see, ordered by their ID (primary key)
        # It is also filtered on the specific module edition of this page and whether or not the given part has a test.
        # If they don't have a test, they won't be included in the queryset.
        module_parts = ModulePart.objects \
            .prefetch_related('test_set') \
            .filter(Q(module_edition__coordinators__user=self.request.user) | Q(teachers__user=self.request.user),
                    Q(module_edition=mod_ed), Q(test__isnull=False)) \
            .order_by('id').distinct()

        # Gather all tests the user is allowed to see, ordered by the ID of their respective module part.
        tests = Test.objects \
            .filter(module_part__in=module_parts) \
            .order_by('module_part__id').distinct()

        # Gather all important information about students and their grades.
        # It returns a dictionary of values, denoted by the .values().
        # It filters the queryset by filtering on students which are following the specified module edition.
        # It orders the result by the person id and further order it on the test id of the grades.
        dicts = Studying.objects \
            .prefetch_related('person', 'study', 'person__Submitter') \
            .values('study__name', 'study__abbreviation', 'person', 'person__name', 'person__university_number',
                    'person__Submitter', 'person__Submitter__grade', 'person__Submitter__test',
                    'person__Submitter__released') \
            .filter(module_edition=mod_ed) \
            .order_by('person_id','person__Submitter__test_id', 'person__Submitter__time') \
            .distinct('person_id','person__Submitter__test_id')

        students = dict()
        temp_dict = dict()
        testallreleased = dict()
        grade_dict = OrderedDict()

        # Changing the queryset to something more easily usable.
        QuerySetChanger(dicts, students, temp_dict, testallreleased)

        # Sort the dictionary of grade information.
        for key in sorted(temp_dict):
            grade_dict[key] = temp_dict[key]

        # Add everything to the context.
        context['mod_ed'] = mod_ed
        context['gradedict'] = grade_dict
        context['studentdict'] = students
        context['module_parts'] = module_parts
        context['testallreleased'] = testallreleased
        context['mod_name'] = Module.objects.values('name').get(moduleedition=mod_ed)['name']
        context['tests'] = tests

        return context


class StudentView(generic.DetailView):
    """ The view students will see.
    It will show each module edition with the students' grades, if they are released.
    """
    template_name = 'Grades/student.html'
    model = Person

    # Check if the user is a student.
    # If not, show them an error page.
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Check if the user has a Studying object, identifying them as a student.
        if not Studying.objects.filter(person__user=user, person__id=self.kwargs['pk']):
            raise PermissionDenied()

        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    # Sets the context data to be used in the template.
    def get_context_data(self, **kwargs):
        context = super(StudentView, self).get_context_data(**kwargs)

        # Get the specified person
        person = Person.objects.get(id=self.kwargs['pk'])

        module_parts_dict = dict()
        test_dict = dict()

        # Gather all connected grade objects to the person.
        dicts = Grade.objects \
            .prefetch_related('test') \
            .values('grade', 'released', 'test') \
            .filter(student=person, released=True) \
            .order_by('test', 'time')

        # Gather all modules which the person is studying.
        modules = ModuleEdition.objects \
            .filter(studying__person=person)

        # For each of these modules, gather the module parts and tests.
        for module_edition in modules:
            module_parts = ModulePart.objects \
                .filter(module_edition=module_edition, test__grade__released=True, test__grade__student=person) \
                .order_by('id').distinct()
            tests = Test.objects \
                .filter(module_part__module_edition=module_edition, grade__released=True, grade__student=person) \
                .order_by('module_part__id').distinct()

            module_parts_dict[module_edition] = module_parts
            test_dict[module_edition] = tests

        temp_dict = dict()
        context_dict = OrderedDict()

        # Changing the queryset to something more useable.
        # Makes a dictionary of grades (temp_dict[TEST] = [GRADE])
        # Due to the ordering, the last grade will be the grade passed to the template (CAN IMPROVE)
        for d in dicts:
            temp_dict[d['test']] = d['grade']

        # Sort the dictionary
        for key in sorted(temp_dict):
            context_dict[key] = temp_dict[key]

        # Add everything to the context
        context['student'] = person
        context['modules'] = modules
        context['module_parts'] = module_parts_dict
        context['tests'] = test_dict
        context['gradedict'] = context_dict

        return context


class ModuleStudentView(generic.DetailView):
    """ The view which shows a students' grades tied to a specific module edition.
    This view is meant for module coordinators and teachers. Module coordinators see all module parts,
    teachers only see their respective parts.
    """
    template_name = 'Grades/modulestudent.html'
    model = ModuleEdition

    # Check if the user is a module coordinator or a teacher.
    # If not, show them an error page.
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is a module coordinator or a teacher
        if not ModuleEdition.objects.filter(Q(coordinators__user=user) | (Q(modulepart__teachers__user=user) & Q(modulepart__teacher__role='T')),
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

    # Set the context data used by the template.
    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(ModuleStudentView, self).get_context_data(**kwargs)

        # Get the specified module edition and student.
        mod_ed = ModuleEdition.objects.get(id=self.kwargs['pk'])
        student = Person.objects.get(id=self.kwargs['sid'])

        # Gather the module parts connected to the module edition.
        module_parts = ModulePart.objects \
            .prefetch_related('test_set') \
            .filter(Q(module_edition__coordinators__user=self.request.user) | (Q(teachers__user=user) & Q(teacher__role='T')),
                    Q(module_edition=mod_ed), Q(test__isnull=False)) \
            .order_by('id').distinct()

        # Gather the test connected to the module parts.
        tests = Test.objects \
            .filter(Q(module_part__module_edition__coordinators__user=self.request.user) |
                    Q(module_part__teachers__user=self.request.user), Q(module_part__in=module_parts)) \
            .order_by('module_part__id').distinct()

        # Gather all grade objects connected to the person and the module edition.
        # They are ordered by the ID of their test and furthermore by the date the grade was added.
        dicts = Grade.objects \
            .prefetch_related('test') \
            .values('grade', 'released', 'test') \
            .filter(test__in=tests, student=student) \
            .order_by('test', 'time')

        temp_dict = dict()
        context_dict = OrderedDict()

        # Changing the queryset to something more useable.
        # Creates a dictionary of grades (temp_dict[TEST] = (GRADE, RELEASED)
        for d in dicts:
            temp_dict[d['test']] = (d['grade'], d['released'])

        # Sorts the dictionary.
        for key in sorted(temp_dict):
            context_dict[key] = temp_dict[key]

        # Add everything to the context.
        context['student'] = student
        context['module_parts'] = module_parts
        context['tests'] = tests
        context['gradedict'] = context_dict

        return context


class ModulePartView(generic.DetailView):
    """ The view of a specific module part.
    This view is meant for module coordinators and teachers. Teachers can only see this view if they are the teacher of
    this specific module part. Module coordinators can see this view if the specific module part is part of their module.
    """
    template_name = 'Grades/module_part.html'
    model = ModulePart

    # Check if the user is a module coordinator or a teacher.
    # If not, show them an error page.
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is a module coordinator or a teacher
        if not ModulePart.objects.filter(Q(module_edition__coordinators__user=user) | Q(teachers__user=user),
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

    # Sets the context data used by the template.
    def get_context_data(self, **kwargs):
        context = super(ModulePartView, self).get_context_data(**kwargs)

        # Get the specified module part.
        module_part = ModulePart.objects.get(id=self.kwargs['pk'])

        # Gather all students which are studying this specific module part.
        # The dictionary is sorted by test ID and the date the grade was added.
        dicts = Studying.objects \
            .prefetch_related('person', 'study', 'person__Submitter') \
            .values('study__name', 'study__abbreviation', 'person', 'person__name', 'person__university_number',
                    'person__Submitter', 'person__Submitter__grade', 'person__Submitter__test',
                    'person__Submitter__released') \
            .filter(module_edition__modulepart=module_part) \
            .order_by('person__Submitter__test', 'person__Submitter__time')

        # Gather all tests in the module part, ordered by the date of examination.
        tests = Test.objects \
            .filter(module_part=module_part) \
            .order_by('time')

        students = dict()
        temp_dict = dict()
        testallreleased = dict()
        grade_dict = OrderedDict()

        # Changing the queryset to something more useable.
        QuerySetChanger(dicts, students, temp_dict, testallreleased)

        # Sorts the dictionary
        for key in sorted(temp_dict):
            grade_dict[key] = temp_dict[key]

        # Add everything to the context.
        context['gradedict'] = grade_dict
        context['studentdict'] = students
        context['module_part'] = module_part
        context['testallreleased'] = testallreleased
        context['tests'] = tests
        return context


class TestView(generic.DetailView):
    """ This view shows the grades for a specific test.
    This view is meant for module coordinators and teachers. Teachers can only see this view if they are the teacher of
    the specific module part this test is a part of. Module coordinators can see this view if the specific test
    is part of their module.
    """
    template_name = 'Grades/test.html'
    model = Test

    # Check if the user is a module coordinator or a teacher.
    # If not, show them an error page.
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is a module coordinator or a teacher
        if not Test.objects.filter(
                        Q(module_part__module_edition__coordinators__user=user) | Q(module_part__teachers__user=user),
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

    # Sets the context data used by the template.
    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)

        # Sets the 'change' attribute.
        # Change == False if nothing has been done to the grades.
        # Change == 1 if some grades have been released.
        # Change == 2 if some grades have been retracted.
        if 'change' not in self.request.session.keys():
            context['change'] = False
        elif self.request.session['change'] == 1:
            context['change'] = 'The chosen grade(s) have successfully been released.'
        elif self.request.session['change'] == 2:
            context['change'] = 'The chosen grade(s) have successfully been retracted.'
        self.request.session['change'] = 0

        # Get the specified test.
        test = Test.objects.get(id=self.kwargs['pk'])

        # Gather all students who have done, or should do the test.
        # This dictionary is ordered by the test ID and the date its grade has been added.
        dicts = Studying.objects \
            .prefetch_related('person', 'study', 'person__Submitter') \
            .values('study__name', 'study__abbreviation', 'person', 'person__name', 'person__university_number',
                    'person__Submitter', 'person__Submitter__grade', 'person__Submitter__test',
                    'person__Submitter__released') \
            .filter(module_edition__modulepart__test=test) \
            .order_by('person__Submitter__test', 'person__Submitter__time')

        students = dict()
        temp_dict = dict()
        testallreleased = dict()
        grade_dict = OrderedDict()

        # Changing the queryset to something more useable.
        QuerySetChanger(dicts, students, temp_dict, testallreleased)

        # Sorts the dicitonary.
        for key in sorted(temp_dict):
            grade_dict[key] = temp_dict[key]

        # Adds everything to the context.
        context['gradedict'] = grade_dict
        context['studentdict'] = students
        context['testallreleased'] = testallreleased
        context['test'] = test
        # A check if the user is allowed to export the grades to .xls.
        context['can_export'] = Test.objects.filter(
            module_part__module_edition__coordinators__user=self.request.user).exists()
        # Set whether the user can release/retract grades.
        context['can_release'] = Test.objects.filter(
            module_part__module_edition__coordinators__user=self.request.user).exists()
        return context


def export(request, *args, **kwargs):
    """ The view gotten when trying to export grades to .xls format.
    :param request: The HTML request
    :param args:
    :param kwargs:
    :return:
    """
    user = request.user

    if not Test.objects.filter(module_part__module_edition__coordinators__user=user, id=kwargs['pk']):
        raise PermissionDenied()

    test = Test.objects.get(id=kwargs['pk'])

    # Gather all students who have done the test.
    # This dictionary is ordered by the university ID and the date their grade has been added.
    dicts = Studying.objects \
        .prefetch_related('person', 'study', 'person__Submitter') \
        .values('person__name', 'person__university_number',
                'study__abbreviation',
                'person__Submitter__grade', 'person__Submitter__time') \
        .filter(module_edition__modulepart__test=test) \
        .order_by('person__name', 'person__Submitter__time')

    mod_ed = test.module_part.module_edition

    table = [
        ['Cursus', '{}'.format(mod_ed.module.code), '', '', 'Tijdstip', '{}'.format(test.time)],
        ['Naam', '{}'.format(dicts[0]['study__abbreviation'])],
        ['Collegejaar', '{}'.format(mod_ed.year)],
        ['Toets', '{}'.format(test.name)],
        ['Blok', '{}'.format(mod_ed.block), '', 'Resultaatschaal', ''],
        ['Gelegenheid', ''],
        [''],
        ['Studentnummer', 'Naam', 'Toetsdatum', 'Resultaat', 'Afwijkende catogorie', 'Geldigheidsduur']
    ]

    temp_dict = OrderedDict()
    for d in dicts:
        temp_dict[d['person__university_number'][1:]] = (d['person__name'], d['person__Submitter__grade'],
                                                     d['person__Submitter__time'].date())

    for u_num, details in temp_dict.items():
        table.append(
            ['{}'.format(u_num), '{}'.format(details[0]), '{}'.format(details[2]), '{}'.format(details[1]),
             '-', '-']
        )

    return excel.make_response_from_array(table, file_name='{} MODXX {} {}.xlsx'
                                              .format(dicts[0]['study__abbreviation'], mod_ed.module.code, test.name),
                                              file_type='xlsx')


def release(request, *args, **kwargs):
    """ The view gotten when trying to release/retract grades.
    :param request: Django request
    :param kwargs: Arguments: Module edition key (pk).
    """
    user = request.user

    # Check whether the user is able to release/retract grades.
    if not ModuleEdition.objects.filter(coordinators__user=user, id=kwargs['pk']):
        raise PermissionDenied()

    # Get the action ('release'/'retract')
    action = request.POST['action']

    mail_list = []

    # Loop over every key in the POST
    for key in request.POST:
        # Check whether the current key is a grade checkbox.
        key_search = re.search('check([0-9]+)', key)
        if key_search:
            # Extract the grade.
            grade_id = int(key_search.group(1))
            grade = Grade.objects.get(id=grade_id)

            if action == 'release':
                # Release the grade.
                grade.released = True
                grade.save()
                # Add the connected person to the mail list.
                mail_list.append(make_mail_grade_released(grade.student, user, grade))
                # Set the change variable to 1 to signify that releases were done.
                request.session['change'] = 1
            elif action == 'retract':
                # Retract the grade.
                grade.released = False
                grade.save()
                # Add the connected person to the mail list.
                mail_list.append(make_mail_grade_retracted(grade.student, user, grade))
                # Set the change variable to 2 to signify that retractions were done.
                request.session['change'] = 2

    # Get a connection and send the mails.
    connection = mail.get_connection()
    connection.send_messages(mail_list)

    # Return to the page the user came from.
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def QuerySetChanger(dicts, students, temp_dict, testallreleased=None):
    """ Change a queryset to something more useable.
    :param dicts: The queryset to be changed.
    :param students: An empty dictionary to be filled with student information.
    :param temp_dict: An empty dictionary to be filled with grades.
    :param testallreleased: An empty dictionary to be filled with wether or not a test has all its grades released.
    :return: -
    """
    for d in dicts:
        student = d['person']
        test = d['person__Submitter__test']

        if student not in students.keys():
            students[student] = dict()
        if student not in temp_dict.keys():
            temp_dict[student] = dict()

        # Create the student dictionary.
        students[student]['name'] = d['person__name']
        students[student]['pid'] = d['person__university_number']
        students[student]['study'] = d['study__name']
        students[student]['sstudy'] = d['study__abbreviation']

        # Create the grade dictionary.
        temp_dict[student][test] = (
            d['person__Submitter__grade'], d['person__Submitter__released'])

        # Create the test released dictionary.
        if not testallreleased == None:
            if not test in testallreleased.keys():
                testallreleased[test] = True
            if not d['person__Submitter__released']:
                testallreleased[test] = False