import re
from collections import OrderedDict

import time
from django.core.exceptions import PermissionDenied
from django.db.models import Case, IntegerField
from django.db.models import Q, Count, Sum
from django.db.models import When
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views import generic, View
import django_excel as excel
from django.views.generic import FormView

from Grades import mailing
from Grades.mailing import mail_module_edition_participants
from dashboard.forms import EmailPreviewForm
from permission_utils import is_coordinator_of_module, u_is_coordinator_of_module, is_study_adviser_of_study
from .models import Studying, Person, ModuleEdition, Test, ModulePart, Grade, Module, Study, Coordinator, Teacher


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
        studying = Studying.objects.filter(~Q(person__teacher__role='A'), person__user=request.user)
        if studying:
            return redirect('grades:student', studying[0].person.id)

        # Check if the user is a module coordinator or a teacher

        if not ModuleEdition.objects.filter(Q(coordinators__user=user) | Q(modulepart__teachers__user=user) | Q(module__study__advisers__user=user)):
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
        module_set = ModuleEdition.objects.filter(
            Q(coordinators__user=user) | Q(modulepart__teachers__user=user) | Q(module__study__advisers__user=user)) \
            .order_by('-year', 'module', 'block') \
            .distinct('year', 'module', 'block')
        return module_set


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
        if not ModuleEdition.objects.filter(Q(coordinators__user=user) | Q(modulepart__teachers__user=user) | Q(module__study__advisers__user=user),
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
                           .filter(Q(module_edition__coordinators__user=self.request.user) | Q(teachers__user=self.request.user) |
                                   Q(module_edition__module__study__advisers__user=self.request.user),
                                   Q(module_edition=mod_ed), Q(test__isnull=False)) \
                           .order_by('id')

        # Gather all tests the user is allowed to see, ordered by the ID of their respective module part.
        tests = Test.objects \
            .filter(Q(type='E') | Q(type='P'),
                    Q(module_part__module_edition__coordinators__user=self.request.user) | Q(module_part__teachers__user=self.request.user) |
                    Q(module_part__module_edition__module__study__advisers__user=self.request.user),
                    module_part__module_edition=mod_ed) \
            .order_by('module_part__id').distinct()

        assignments = Test.objects \
            .filter(Q(type='A'),
                    Q(module_part__module_edition__coordinators__user=self.request.user) |
                    Q(module_part__teachers__user=self.request.user) |
                    Q(module_part__module_edition__module__study__advisers__user=self.request.user),
                    module_part__module_edition=mod_ed) \
            .order_by('module_part__id').distinct()

        module_parts = ModulePart.objects \
            .filter(id__in=module_parts) \
            .annotate(
            num_ep=Sum(
                Case(When(Q(test__type='E') | Q(test__type='P'), then=1), default=0, output_field=IntegerField()))) \
            .annotate(
            num_a=Sum(Case(When(test__type='A', then=1), default=0, output_field=IntegerField())))

        # Add everything to the context.
        context['mod_ed'] = mod_ed
        context['assignments'] = assignments
        context['module_parts'] = module_parts
        context['mod_name'] = Module.objects.values('name').get(moduleedition=mod_ed)['name']
        context['tests'] = tests
        context['can_edit'] = Coordinator.objects.filter(person__user=self.request.user, module_edition=mod_ed).exists() or Teacher.objects.filter(person__user=self.request.user, module_part__module_edition=mod_ed).exists()

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
        if not (Studying.objects.filter(person__user=user, person__id=self.kwargs['pk']) or\
            Study.objects.filter(advisers__user=user, modules__moduleedition__studying__person__id=self.kwargs['pk'])):
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
        tests_dict = dict()
        grades_dict = dict()
        assignments_dict = dict()
        name_override_dict = dict()

        grades_list = Grade.objects \
            .prefetch_related('test') \
            .filter(student=person, test__released=True) \
            .values('grade', 'test') \
            .order_by('test_id', '-id') \
            .distinct('test_id')

        for grade in grades_list:
            grades_dict[grade['test']] = grade['grade']

        modules_list = ModuleEdition.objects \
            .filter(studying__person=person) \
            .order_by('id')

        for module in modules_list:
            module_parts_list = ModulePart.objects \
                .prefetch_related('test_set') \
                .filter(module_edition=module, test__released=True) \
                .order_by('id') \
                .distinct('id')

            for module_part in module_parts_list:
                tests = module_part.test_set \
                    .filter(Q(type='E') | Q(type='P'), released=True) \
                    .order_by('module_part__id','id')

                assignments = list(module_part.test_set \
                    .filter(type='A', released=True) \
                    .order_by('module_part__id','id'))

                tests_dict[module_part] = tests

                streak = 0
                start = None
                current = ""
                remove_list = []

                for assignment in assignments:
                    if assignment.id in grades_dict and grades_dict[assignment.id] == 1.0:
                        if streak > 0:
                            current = str(start.name) + " to " + str(assignment.name)
                            remove_list.append(assignment)
                            streak += 1
                        else:
                            start = assignment
                            streak = 1
                    else:
                        remove_list.append(assignment)
                        if streak > 0:
                            if streak > 1:
                                name_override_dict[start] = current
                            streak = 0
                            start = None

                if streak > 1:
                    name_override_dict[start] = current

                for remove in remove_list:
                    assignments.remove(remove)

                assignments_dict[module_part] = assignments

            module_parts_dict[module] = module_parts_list

        # Add everything to the context
        context['studentname'] = person.name
        context['modules'] = modules_list
        context['module_parts'] = module_parts_dict
        context['tests'] = tests_dict
        context['grades'] = grades_dict
        context['assignments'] = assignments_dict
        context['name_override'] = name_override_dict

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
        if not ModuleEdition.objects.filter(Q(coordinators__user=user) | Q(modulepart__teachers__user=user) | Q(module__study__advisers__user=user),
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
            .filter(
            Q(module_edition__coordinators__user=self.request.user) | Q(teachers__user=user) | Q(module_edition__module__study__advisers__user=user),
            Q(module_edition=mod_ed), Q(test__isnull=False)) \
            .order_by('id').distinct()

        # Gather the test connected to the module parts.
        tests = Test.objects \
            .filter(Q(type='E') | Q(type='P'), module_part__in=module_parts) \
            .order_by('module_part__id').distinct()

        assignments = Test.objects \
            .filter(type='A', module_part__in=module_parts) \
            .order_by('module_part__id').distinct()

        # Gather all grade objects connected to the person and the module edition.
        # They are ordered by the ID of their test and furthermore by the date the grade was added.
        dicts = Grade.objects \
            .prefetch_related('test') \
            .values('grade', 'released', 'test') \
            .filter(Q(test__in=tests) | Q(test__in=assignments), student=student) \
            .order_by('test_id', '-id') \
            .distinct('test_id')

        temp_dict = dict()
        context_dict = OrderedDict()

        # Changing the queryset to something more useable.
        # Creates a dictionary of grades (temp_dict[TEST] = (GRADE, RELEASED)
        for d in dicts:
            temp_dict[d['test']] = (d['grade'], d['released'])

        # Sorts the dictionary.
        for key in sorted(temp_dict):
            context_dict[key] = temp_dict[key]

        module_parts = ModulePart.objects \
            .filter(id__in=module_parts) \
            .annotate(
                num_ep=Sum(Case(When(Q(test__type='E') | Q(test__type='P'), then=1), default=0, output_field=IntegerField()))) \
            .annotate(
                num_a=Sum(Case(When(test__type='A', then=1), default=0, output_field=IntegerField())))

        # Add everything to the context.
        context['student'] = student
        context['module_parts'] = module_parts
        context['tests'] = tests
        context['mod_ed'] = mod_ed
        context['assignments'] = assignments
        context['gradedict'] = context_dict
        context['can_edit'] = Coordinator.objects.filter(person__user=self.request.user,
                                                         module_edition=mod_ed).exists() or Teacher.objects.filter(
            person__user=self.request.user, module_part__module_edition=mod_ed).exists()

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
        if not ModulePart.objects.filter(Q(module_edition__coordinators__user=user) | Q(teachers__user=user) | Q(module_edition__module__study__advisers__user=user),
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

        # Gather all tests in the module part, ordered by the date of examination.
        tests = Test.objects \
            .filter(Q(type='E') | Q(type='P'), module_part=module_part) \
            .order_by('module_part__id').distinct()

        assignments = Test.objects \
            .filter(type='A', module_part=module_part) \
            .order_by('module_part__id').distinct()

        students = dict()

        # Add everything to the context.
        context['studentdict'] = students
        context['module_part'] = module_part
        context['tests'] = tests
        context['mod_name'] = module_part.module_edition.module.name
        context['assignments'] = assignments
        context['can_edit'] = Coordinator.objects.filter(person__user=self.request.user,
                                                         module_edition__modulepart=module_part).exists() or Teacher.objects.filter(
            person__user=self.request.user, module_part__module_edition__modulepart=module_part).exists()

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
                        Q(module_part__module_edition__coordinators__user=user) | Q(module_part__teachers__user=user) | Q(module_part__module_edition__module__study__advisers__user=user),
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
            context['change'] = 1
        elif self.request.session['change'] == 2:
            context['change'] = 2
        self.request.session['change'] = 0

        # Get the specified test.
        test = Test.objects.get(id=self.kwargs['pk'])

        students = dict()

        # Adds everything to the context.
        context['studentdict'] = students
        context['test'] = test
        # A check if the user is allowed to export the grades to .xls.
        context['can_export'] = Test.objects.filter(
            module_part__module_edition__coordinators__user=self.request.user).exists()
        # Set whether the user can release/retract grades.
        context['can_release'] = Test.objects.filter(
            module_part__module_edition__coordinators__user=self.request.user).exists()
        context['can_edit'] = Coordinator.objects.filter(person__user=self.request.user,
                                                         module_edition__modulepart__test=test).exists() or Teacher.objects.filter(
            person__user=self.request.user, module_part__module_edition__modulepart__test=test).exists()

        return context


class EmailBulkTestReleasedPreviewView(FormView):
    """Email view used to email students about a bulk-release of grades (multiple grades released at once.)

    Use the argument tests to pass Test instances that have been released.
    """
    template_name = 'Grades/email_preview.html'
    form_class = EmailPreviewForm
    tests = []

    def __init__(self, *args, **kwargs):
        instance = super(EmailGradeReleasedPreviewView, self).__init__(self, *args, **kwargs)
        instance.tests = kwargs['tests']

    # Check permissions
    def dispatch(self, request, *args, **kwargs):
        test = get_object_or_404(Test, pk=kwargs['pk'])
        person = Person.objects.filter(user=self.request.user)
        if is_coordinator_of_module(person, test.module_part.module_edition):
            return super(EmailGradeReleasedPreviewView, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied("You are not allowed to send emails to students.")

    def get_initial(self):
        test = Test.objects.filter(pk=self.kwargs['pk']).prefetch_related('module_part__module_edition__module').first()
        return {'test': test.pk,
                'subject': '[SETH] {} ({}-{}) Grades released.'.format(test.module_part.module_edition.module.name, test.module_part.module_edition.year,
                                                              test.module_part.module_edition.block),
                'message': 'Dear student, \n\nThe grades for some tests have been released. Go to {} to see your '
                           'grades.\n\n Tests affected:\n' + ''.join(['{}\n'.format(test.name) for test in self.tests])
                           + '\n\nKind regards,\n\n{}\n\n=======================================\n'
                           'SETH is in BETA. Only grades released in OSIRIS are official. No rights can be derived from'
                           ' grades or any other kinds of information in this system.'
                           .format(mailing.DOMAIN, Person.objects.get(user=self.request.user).name)}

    def form_valid(self, form):
        test = get_object_or_404(Test, pk=self.kwargs['pk'])
        failed = mail_module_edition_participants(
            module_edition=test.module_part.module_edition,
            subject=form.cleaned_data['subject'],
            body=form.cleaned_data['message'])
        if failed:
            return HttpResponse('Sending of the email failed for: \n{}'.format(
                ['{}\t{}\n'.format(student.university_number, student.name) for student in failed]
            ))
        else:
            return redirect('grades:test', test.pk)

    def get_context_data(self, **kwargs):
        context = super(EmailGradeReleasedPreviewView, self).get_context_data(**kwargs)
        context['pk'] = context['view'].kwargs['pk']
        return context



class EmailGradeReleasedPreviewView(FormView):
    template_name = 'Grades/email_preview.html'
    form_class = EmailPreviewForm

    # Check permissions
    def dispatch(self, request, *args, **kwargs):
        test = get_object_or_404(Test, pk=kwargs['pk'])
        person = Person.objects.filter(user=self.request.user)
        if is_coordinator_of_module(person, test.module_part.module_edition):
            return super(EmailGradeReleasedPreviewView, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied("You are not allowed to send emails to students.")

    def get_initial(self):
        test = Test.objects.filter(pk=self.kwargs['pk']).prefetch_related('module_part__module_edition__module').first()
        return {'test': test.pk,
                'subject': '[SETH] {} ({}-{}) Grade released: {}'.format(test.module_part.module_edition.module.name, test.module_part.module_edition.year,
                                                              test.module_part.module_edition.block, test.name),
                'message': 'Dear student, \n\nThe grades for test {} have been released. Go to {} to see your '
                           'grade.\n\nKind regards,\n\n{}\n\n=======================================\n'
                           'SETH is in BETA. Only grades released in OSIRIS are official. No rights can be derived from'
                           ' grades or any other kinds of information in this system.'.format(test.name, mailing.DOMAIN, Person.objects.get(user=self.request.user).name)}

    def form_valid(self, form):
        test = get_object_or_404(Test, pk=self.kwargs['pk'])
        failed = mail_module_edition_participants(
            module_edition=test.module_part.module_edition,
            subject=form.cleaned_data['subject'],
            body=form.cleaned_data['message'])
        if failed:
            return HttpResponse('Sending of the email failed for: \n{}'.format(
                ['{}\t{}\n'.format(student.university_number, student.name) for student in failed]
            ))
        else:
            return redirect('grades:test', test.pk)

    def get_context_data(self, **kwargs):
        context = super(EmailGradeReleasedPreviewView, self).get_context_data(**kwargs)
        context['pk'] = context['view'].kwargs['pk']
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
        .prefetch_related('person', 'person__Submitter') \
        .values('person__name', 'person__university_number') \
        .filter(module_edition__modulepart__test=test) \
        .order_by('person__name')

    grades = Grade.objects \
        .filter(test=test) \
        .order_by('time')

    study = Study.objects \
        .get(modules__moduleedition__modulepart__test=test)

    mod_ed = test.module_part.module_edition

    table = [
        ['Cursus', '{}'.format(mod_ed.module.code), '', '', 'Tijdstip', 'N/A'],
        ['Collegejaar', '{}'.format(mod_ed.year)],
        ['Toets', '{}'.format(test.name)],
        ['Blok', '{}'.format(mod_ed.block), '', 'Resultaatschaal', ''],
        ['Gelegenheid', ''],
        [''],
        ['Studentnummer', 'Naam', 'Toetsdatum', 'Resultaat', 'Afwijkende categorie', 'Geldigheidsduur']
    ]

    temp_dict = OrderedDict()
    grade_dict = dict()
    for grade in grades:
        grade_dict[grade.student.university_number] = grade.grade

    for d in dicts:
        temp_dict[d['person__university_number'][1:]] = d['person__name']

    for u_num, name in temp_dict.items():
        if ('s' + u_num) in grade_dict.keys():
            table.append(
                ['{}'.format(u_num), '{}'.format(name), 'N/A', '{}'.format(grade_dict['s' + u_num]), 'N/A', 'N/A']
            )
        else:   # University Number, Student name, Date, Grade, Category, Validity period
            table.append(
                ['{}'.format(u_num), '{}'.format(name), 'N/A', 'NVD', 'N/A', 'N/A']
            )

    return excel.make_response_from_array(table, file_name='{} MODXX {} {}.xlsx'
                                          .format(study.abbreviation, mod_ed.module.code, test.name),
                                          file_type='xlsx')


def release(request, *args, **kwargs):
    """ The view gotten when trying to release/retract grades.
    :param request: Django request
    :param kwargs: Arguments: Module edition key (pk).
    """
    user = request.user

    # Check whether the user is able to release/retract grades.
    tests = Test.objects.prefetch_related('grade_set').filter(module_part__module_edition__coordinators__user=user,
                                                          id=kwargs['pk'])
    if not tests:
        raise PermissionDenied()

    test = tests[0]

    if not 'rel' in request.POST:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.POST['rel'] == "False":
        test.released = True
        test.save()
        request.session['change'] = 1
        if 'sendcheck' in request.POST:
            return redirect('grades:test_send_email', test.id)

    else:
        test.released = False
        test.save()
        request.session['change'] = 2

    # Return to the page the user came from.
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def remove(request, *args, **kwargs):

    user = request.user

    test = Test.objects.prefetch_related('grade_set').get(module_part__module_edition__coordinators__user=user,
                                                          id=kwargs['pk'])
    if not test:
        raise PermissionDenied()

    data = {}

    student = kwargs['sid']
    test.grade_set.filter(student=student).delete()

    data = {
        'deleted': not test.grade_set.filter(student=student).exists()
    }

    # Return to the page the user came from.
    return JsonResponse(data)


def edit(request, *args, **kwargs):

    user = request.user

    tests = Test.objects.prefetch_related('grade_set').filter(Q(module_part__module_edition__coordinators__user=user) |
                                                          Q(module_part__teachers__user=user),
                                                          id=kwargs['pk']).distinct()
    if not tests:
        raise PermissionDenied()

    test = tests[0]

    data = {}

    if request.POST:
        student = kwargs['sid']
        g = test.grade_set.create(student_id=student,
                              teacher=Person.objects.get(user=user),
                              test=test,
                              grade=request.POST.get('grade', None),
                              description="")

        data = {
            'grade': g.grade
        }

    # Return to the page the user came from.
    return JsonResponse(data)


def get(request, *args, **kwargs):
    user = request.user

    if request.method == "GET":

        data_array = []

        (mod_ed, query_result) = create_grades_query(request.GET.get('view'), kwargs['pk'], user, (kwargs['t']) if kwargs['t'] else None)

        student_grades_exam = OrderedDict()
        for student in query_result:
            if student.person_id is None:
                continue

            key = "<a href={}>{} ({})</a>".format(
                reverse('grades:modstudent', kwargs={'pk': mod_ed.id, 'sid': student.person_id}),
                student.name, student.university_number)

            if (student.type == 'E' or student.type == 'P'):
                value = '<a id="grade_{}_{}"' \
                        'data-grade="{}"'\
                        'data-grade-min="{}" data-grade-max="{}"' \
                        'data-edit-url="{}" ' \
                        'data-remove-url="{}"' \
                        '>{}</a>'.format(student.person_id, student.test_id,
                                         (student.grade if student.grade else '-'),
                                         student.minimum_grade, student.maximum_grade,
                                         reverse('grades:edit', kwargs={'pk': student.test_id, 'sid': student.person_id}),
                                         reverse('grades:remove', kwargs={'pk': student.test_id, 'sid': student.person_id}),
                                         (student.grade if student.grade else '-'))
            else:
                if student.grade == 1:
                    val = 'done'
                else:
                    val = 'clear'
                value = '<a id="grade_{}_{}"' \
                        'data-grade="{}"' \
                        'data-always-color="True"' \
                        'data-grade-min="{}" data-grade-max="{}"' \
                        'data-url="{}" ' \
                        '><i class="material-icons">{}</i></a>'.format(student.person_id, student.test_id,
                                         (student.grade if student.grade else '0'),
                                         student.minimum_grade, student.maximum_grade,
                                         reverse('grades:edit',
                                                 kwargs={'pk': student.test_id, 'sid': student.person_id}),
                                         val)

            if not key in student_grades_exam.keys():
                student_grades_exam[key] = []
            student_grades_exam[key].append(value)

        for key, value in student_grades_exam.items():
            data_array.append([key] + value)

        data = {
            "data": data_array
        }

    # Return to the page the user came from.
    return JsonResponse(data)


def create_grades_query(view, pk, user, type=None):
    """
    Creates a SQL query to get all grades from all students of a certain module edition, module part or test.
    The result of the query can be looped over and the field present are:
        Person:     person_id, name, university_number,
        ModulePart: module_part_id,
        Test:       minimum_grade, maximum_grade, test_id, type,
        Grade:      grade, id
    :param view: The component from which to get the grade - ('mod_ed', 'mod_part', 'mod_test').
    :param pk: The ID of the component.
    :param user: The user issuing the query.
    :param type: The type of the test to be returned by the query. Can be omitted.
    :return: (mod_ed, query_result) - The corresponding module edition and the result of the query. Returns None if a correct view isn't specified.
    """
    if type == 'A':
        type = "type='A'"
    elif type == 'E' or type =='P':
        type = "type='E' OR type='P'"
    else:
        type = ""

    if view == 'mod_ed':
        mod_eds = ModuleEdition.objects.filter(Q(coordinators__user=user) |
                                              Q(modulepart__teachers__user=user) |
                                              Q(module__study__advisers__user=user),
                                              pk=pk).distinct()
        if not mod_eds:
            raise PermissionDenied()

        mod_ed = mod_eds[0]

        module_parts = str(ModulePart.objects \
                           .filter(Q(module_edition__coordinators__user=user) | Q(teachers__user=user) |
                                   Q(module_edition__module__study__advisers__user=user),
                                   Q(module_edition=mod_ed), Q(test__isnull=False)) \
                           .values('id') \
                           .order_by('id').distinct().query)

        in_test = "IN (SELECT id FROM \"Grades_test\" WHERE module_part_id IN (" + module_parts + ")) "
        where_test = "module_part_id IN (" + module_parts + ")"
        if type != "":
            where_test += " AND (" + type + ") "

    elif view == 'mod_part':
        mod_eds = ModuleEdition.objects.filter(Q(coordinators__user=user) |
                                              Q(modulepart__teachers__user=user) |
                                              Q(module__study__advisers__user=user),
                                              modulepart__pk=pk) \
            .distinct()
        if not mod_eds:
            raise PermissionDenied()

        mod_ed = mod_eds[0]

        in_test = "IN (SELECT id FROM \"Grades_test\" WHERE module_part_id = " + pk + ") "
        where_test = "module_part_id = " + pk
        if type != "":
            where_test += " AND (" + type + ") "

    elif view == 'mod_test':
        mod_eds = ModuleEdition.objects.filter(Q(coordinators__user=user) |
                                              Q(modulepart__teachers__user=user) |
                                              Q(module__study__advisers__user=user),
                                              modulepart__test__pk=pk) \
            .distinct()
        if not mod_eds:
            raise PermissionDenied()

        mod_ed = mod_eds[0]

        in_test = "= " + pk + " "
        where_test = "T.id = " + pk + " "

    else:
        return None

    query_result = Grade.objects.raw(
        "SELECT S.person_id, P.name, P.university_number, T.module_part_id, T.minimum_grade, T.maximum_grade, T.id AS test_id, T.type, G.grade, G.id "
        "FROM \"Grades_test\" T FULL OUTER JOIN ( "
        "SELECT person_id FROM \"Grades_studying\" "
        "WHERE module_edition_id = %s "
        ") AS S "
        "ON TRUE LEFT JOIN ( "
        "SELECT DISTINCT ON (test_id, student_id) id, test_id, student_id, grade "
        "FROM \"Grades_grade\" "
        "WHERE test_id " + in_test +
        "ORDER BY student_id, test_id, id DESC "
        ") AS G "
        "ON G.test_id = T.id AND G.student_id = S.person_id "
        "FULL OUTER JOIN \"Grades_person\" P "
        "ON P.id = S.person_id "
        "WHERE " + where_test +
        "ORDER BY P.name, S.person_id, T.module_part_id, T.type, T.id, G.id DESC ;",
        [mod_ed.id]
    )

    return (mod_ed, query_result)


def QuerySetChanger(dicts, grade_dict, testallreleased=None):
    """ Change a queryset to something more useable.
    :param dicts: The queryset to be changed.
    :param students: An empty dictionary to be filled with student information.
    :param temp_dict: An empty dictionary to be filled with grades.
    :param testallreleased: An empty dictionary to be filled with whether or not a test has all its grades released.
    :return: -
    """
    for d in dicts:
        student = (d['person'], d['person__name'], d['person__university_number'])
        test = d['person__Submitter__test']

        if student not in grade_dict.keys():
            grade_dict[student] = dict()

        # Create the grade dictionary.
        grade_dict[student][test] = (
            d['person__Submitter__grade'], d['person__Submitter__released'])

        # Create the test released dictionary.
        if not testallreleased == None:
            if not test in testallreleased.keys():
                testallreleased[test] = True
            if not d['person__Submitter__released']:
                testallreleased[test] = False