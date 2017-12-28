from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.db import transaction
from django.db.utils import IntegrityError
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponse, \
    Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import generic, View
from django.utils import timezone
from django.db.models import Q
import django_excel as excel
from django.views.decorators.http import require_http_methods, require_GET
from permission_utils import *

from dashboard.views import bad_request

import re

from Grades.exceptions import GradeException
from Grades.models import ModuleEdition, Grade, Test, Person, ModulePart, Studying, Module, Study
from importer.forms import GradeUploadForm, TestGradeUploadForm, ImportStudentForm, ImportStudentModule, \
    ImportModuleEditionStructureForm, COLUMN_TITLE_ROW


# Create your views here.
class ImporterIndexView(LoginRequiredMixin, View):
    """Index view of the importer module. Serves both Module Coordinators and Teachers.

    Module coordinators are presented with an overview of the module editions they are a coordinator of, for which they
    can perform administrative actions. They can add students to a module edition, and download and upload a form that
    contains grades for the tests which are in the module. This can be done for the whole module, or per test individually.

    Teachers receive a list of module parts that are a teacher of, with their tests. They can, like module coordinators,
    download and upload an excel sheet that contains grades. This can be done per test individually.
    """
    model = ModuleEdition

    def get(self, request, *args, **kwargs):
        context = dict()
        # context['is_module_coordinator'] = False
        # context['is_teacher'] = False
        coordinator_or_teacher = False

        if ModuleEdition.objects.filter(coordinators__user=self.request.user):
            # context['is_module_coordinator'] = True
            context['module_editions_list'] = self.make_modules_context()
            coordinator_or_teacher = True
        if ModulePart.objects.filter(teacher__person__user=self.request.user):
            # context['is_teacher'] = True
            context['module_parts_list'] = self.make_module_parts_context()
            coordinator_or_teacher = True
        if not coordinator_or_teacher:
            raise PermissionDenied('Only module coordinators or teachers can view this page.')
        return render(request, 'importer/mcindex2.html', context)

    def make_modules_context(self):
        module_editions = ModuleEdition.objects.filter(coordinator__person__user=self.request.user).prefetch_related(
            'modulepart_set__test_set')

        context = dict()
        context['module_editions'] = []
        for module_edition in module_editions:
            edition = {'name': module_edition, 'pk': module_edition.pk, 'module_parts': []}
            for module_part in module_edition.modulepart_set.all():
                part = {'name': module_part.name, 'pk': module_part.pk, 'tests': []}
                sign_off_assignments = []
                for test in module_part.test_set.all():
                    if test.type is 'A':
                        sign_off_assignments.append(test)
                        continue
                    test_item = {'name': test.name, 'pk': test.pk, 'signoff': False}
                    part['tests'].append(test_item)
                if sign_off_assignments:
                    soa_line = {'module_part_pk': module_part.pk, 'signoff': True}
                    if len(sign_off_assignments) > 1:
                        soa_line['name'] =  'S/O assignments {} to {}'.format(sign_off_assignments[0].name,
                                                                  sign_off_assignments[-1].name)
                    else:
                        soa_line['name'] =  'S/O assignment {}'.format(sign_off_assignments[0].name)
                    part['tests'].append(soa_line)
                edition['module_parts'].append(part)

            context['module_editions'].append(edition)
        return context

    def make_module_parts_context(self):
        module_parts =  ModulePart.objects.filter(teacher__person__user=self.request.user).prefetch_related(
            'test_set')

        context = dict()
        context['module_parts'] = []
        for module_part in module_parts:
            part = {'name': module_part.name, 'pk': module_part.pk, 'module_edition': module_part.module_edition, 'tests': []}
            sign_off_assignments = []
            for test in module_part.test_set.all():
                if test.type is 'A':
                    sign_off_assignments.append(test)
                    continue
                test_item = {'name': test.name, 'pk': test.pk, 'signoff': False}
                part['tests'].append(test_item)
            if sign_off_assignments:
                soa_line = {'module_part_pk': module_part.pk, 'signoff': True}
                if len(sign_off_assignments) > 1:
                    soa_line['name'] =  'S/O assignments {} to {}'.format(sign_off_assignments[0].name,
                                                              sign_off_assignments[-1].name)
                else:
                    soa_line['name'] =  'S/O assignment {}'.format(sign_off_assignments[0].name)
                part['tests'].append(soa_line)
            context['module_parts'].append(part)

        return context


@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def import_module(request, pk):
    """Module import. Use an .xlsx file to submit grades to a module edition

    On GET the user is presented with a file upload form.

    On POST, the submitted .xlsx file is processed by the system, registering Grade object for each grade in the excel
    file. It dynamically detects the tests that are submitted (by exact name match or database ID), and omits extra
    columns silently. Also, lines that do not have a filled in student number are ignored. Students that are not
    declared as part of the module (def:import_student_to_module) raise an import error.

    :param request: Django request
    :param pk: Module that grades should be submitted to
    :return: A redirect to the Grades module's module view on success. Otherwise a 404 (module does not exist), 403
        (no permissions) or 400 (bad excel file or other import error)
    """
    person = Person.objects.filter(user=request.user).first()
    module_edition = get_object_or_404(ModuleEdition, pk=pk)
    if not is_coordinator_or_assistant_of_module(person, module_edition):
        raise PermissionDenied('You are not the module coordinator for this course')

    if request.method == "POST":
        form = GradeUploadForm(request.POST, request.FILES)

        if form.is_valid():
            title_row = form.cleaned_data.get('title_row') - 1

            # Check if /any/ tests and/or grades are imported.
            any_tests = False

            sheet = request.FILES['file'].get_book_dict()
            for table in sheet:
                # Check if the sheet has enough rows
                if title_row >= len(sheet[table]) :
                    return bad_request(request, {'message': 'The file that was uploaded was not recognised as a grade '
                                                            'excel file. Are you sure the file is an .xlsx file, and '
                                                            'that all fields are present? Otherwise, download a new '
                                                            'gradesheet and try using that instead.'})

                test_rows = dict()

                university_number_field = None

                # Detect university_number and test columns
                for title_index in range(0, len(sheet[table][title_row])):
                    # This is the university number column
                    if 'number' in str(sheet[table][title_row][title_index]).lower():
                        university_number_field = title_index
                    else:
                        # Attempt to find a Test

                        # search by ID
                        try:
                            test = Test.objects.filter(
                                pk=sheet[table][title_row][title_index])
                            if test:
                                if not test.filter(module_part__module_edition=module_edition):
                                    return bad_request(request, {'message': 'Attempt to register grades for a test that'
                                                                            ' is not part of this module.'})
                                test_rows[title_index] = sheet[table][title_row][title_index]  # pk of Test
                                any_tests = True
                        except (ValueError, TypeError):
                            # search by name
                            if Test.objects.filter(
                                    name=sheet[table][title_row][title_index]
                            ).filter(module_part__module_edition=pk):
                                test_rows[title_index] = Test.objects.filter(
                                    name=sheet[table][title_row][title_index]
                                ).filter(module_part__module_edition=pk)[0].pk  # pk of Test
                                any_tests = True
                            # Else not a test, continue...

                if university_number_field is None:
                    continue  # Ignore this sheet
                if len(test_rows.keys()) == 0:
                    continue  # Ignore this sheet


                # The current user's Person is the corrector of the grades.
                teacher = Person.objects.filter(user=request.user).first()

                grades = []

                # Retrieve Test object beforehand to validate permissions on tests and speed up Grade creation
                tests = dict()
                for test_column in test_rows.keys():
                    tests[test_column] = Test.objects.get(pk=test_rows[test_column])

                # Check excel file for invalid students
                invalid_students = []
                for row in sheet[table][(title_row + 1):]:
                    if not Studying.objects.filter(person__university_number=row[university_number_field]).filter(
                            module_edition=pk):
                        invalid_students.append(row[university_number_field])
                # Check for invalid student numbers in the university_number column, but ignore empty fields.
                if [student for student in invalid_students if student is not '']:
                    return bad_request(request, {'message': 'Students {} are not enrolled in this module. '
                                                            'Enroll these students first before retrying.'
                                                            .format(invalid_students)})

                # Make Grades
                for row in sheet[table][(title_row + 1):]:  # Walk horizontally over table
                    student = Person.objects.filter(university_number=row[university_number_field]).first()
                    # check if this is not an empty line, else continue.
                    if student:
                        for test_column in test_rows.keys():
                            try:
                                grades.append(make_grade(
                                    student=student,
                                    corrector=teacher,
                                    test=tests[test_column],
                                    grade=row[test_column]
                                ))
                            except GradeException as e:  # Called for either: bad grade, grade out of bounds
                                return HttpResponseBadRequest(e)
                save_grades(grades)  # Bulk-save grades. Also prevents a partial import of the sheet.


            # Check if anything was imported.
            if not any_tests:
                return bad_request(request, {'message': 'There were no tests recognized to import.'})

            return redirect('grades:gradebook', pk)
        else:
            return bad_request(request, {'message': 'The file that was uploaded was not recognised as a grade excel '
                                                    'file. Are you sure the file is an .xlsx file? Otherwise, download '
                                                    'a new gradesheet and try using that instead.'})
    else:  # GET request
        form = GradeUploadForm()
        return render(request, 'importer/importmodule.html', {'form': form, 'pk': pk})


@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def import_module_part(request, pk):
    """Module part import. Use an .xlsx file to submit grades to a module part

    On GET the user is presented with a file upload form.

    On POST, the submitted .xlsx file is processed by the system, registering Grade object for each grade in the excel
    file. It dynamically detects the tests that are submitted (by exact name match or database ID), and omits extra
    columns silently. Also, lines that do not have a filled in student number are ignored. Students that are not
    declared as part of the module (def:import_student_to_module) raise an import error.

    :param request: Django request
    :param pk: Module part that grades should be submitted to
    :return: A redirect to the Grades course view on success. Otherwise a 404 (module does not exist), 403
        (no permissions) or 400 (bad excel file or other import error)
    """
    module_part = get_object_or_404(ModulePart, pk=pk)
    module_edition = get_object_or_404(ModuleEdition, modulepart=module_part)

    person = Person.objects.filter(user=request.user).filter(
        Q(coordinator__module_edition__modulepart=module_part) | Q(teacher__module_part=module_part)
    ).first()
    if not ModuleEdition.objects.filter(modulepart=module_part):
        raise Http404('Module does not exist.')
    if not (is_coordinator_or_assistant_of_module(person, module_edition) or is_coordinator_or_teacher_of_module_part(person, module_part)):
        raise PermissionDenied('You are not allowed to do this.')

    if request.method == "POST":
        form = GradeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            title_row = form.cleaned_data.get('title_row') - 1

            # Check if /any/ tests and/or grades are imported.
            any_tests = False

            sheet = request.FILES['file'].get_book_dict()
            for table in sheet:
                # Check if the sheet has enough rows
                if title_row >= len(sheet[table]):
                    return bad_request(request, {'message': 'The file that was uploaded was not recognised as a grade'
                                                            ' excel file. Are you sure the file is an .xlsx file, and'
                                                            ' that all fields are present? Otherwise, download a new'
                                                            ' gradesheet and try using that instead.'})

                test_rows = dict()

                university_number_field = None

                # Detect university_number and test columns
                for title_index in range(0, len(sheet[table][title_row])):
                    # This is the university number column
                    if 'number' in str(sheet[table][title_row][title_index]).lower():
                        university_number_field = title_index
                    else:
                        # Attempt to find a Test

                        # search by ID
                        try:
                            test = Test.objects.filter(
                                pk=sheet[table][title_row][title_index])
                            if test:
                                if not test.filter(module_part=module_part):
                                    return bad_request(request, {'message': 'Attempt to register grades for a test that'
                                                                            ' is not part of this module'})
                                test_rows[title_index] = sheet[table][title_row][title_index]  # pk of Test
                                any_tests = True
                        except (ValueError, TypeError):
                            pass  # Not an int.
                        # search by name
                        if Test.objects.filter(module_part=module_part).filter(
                                name=sheet[table][title_row][title_index]):
                            test_rows[title_index] = Test.objects.filter(
                                name=sheet[table][title_row][title_index]
                            ).filter(module_part=module_part)[0].pk  # pk of Test
                            any_tests = True

                        # Attempt to ignore test altogether.
                        else:
                            pass

                if university_number_field is None:
                    continue  # Ignore this sheet
                if len(test_rows.keys()) == 0:
                    continue  # Ignore this sheet

                # The current user's Person is the corrector of the grades.
                teacher = Person.objects.filter(user=request.user).first()

                grades = []

                # Retrieve Test object beforehand to validate permissions on tests and speed up Grade creation
                tests = dict()
                for test_column in test_rows.keys():
                    tests[test_column] = Test.objects.get(pk=test_rows[test_column])

                # Check excel file for invalid students
                invalid_students = []
                for row in sheet[table][(title_row + 1):]:
                    if not Studying.objects.filter(person__university_number__contains=row[university_number_field]).filter(
                            module_edition=module_edition):
                        invalid_students.append(row[university_number_field])
                # Check for invalid student numbers in the university_number column, but ignore empty fields.
                if [student for student in invalid_students if student is not '']:
                    return bad_request(request, {'message': 'Students {} are not enrolled in this module.\n '
                                                            'Enroll these students first before retrying'
                                                            .format(invalid_students)})

                # Make Grades
                for row in sheet[table][(title_row + 1):]:  # Walk horizontally over table
                    student = Person.objects.filter(university_number__contains=row[university_number_field]).first()
                    # check if this is not an empty line, else continue.
                    if student:
                        for test_column in test_rows.keys():
                            try:
                                grades.append(make_grade(
                                    student=student,
                                    corrector=teacher,
                                    test=tests[test_column],
                                    grade=row[test_column]
                                ))
                            except GradeException as e:  # Called for either: bad grade, grade out of bounds
                                return bad_request(request, {'error': e})
                save_grades(grades)  # Bulk-save grades. Also prevents a partial import of the sheet.

            # Check if anything was imported.
            if not any_tests:
                return bad_request(request, {'message': 'There were no tests recognized to import.'})
            return redirect('grades:module_part', pk)
        else:
            return bad_request(request, {'message': 'The file uploaded was not recognised as a grade excel file.'
                                                    ' Are you sure the file is an .xlsx file? Otherwise, download a new'
                                                    ' gradesheet and try using that instead'})
    else:  # GET request
        form = GradeUploadForm()
        return render(request, 'importer/importmodulepart.html', {'form': form, 'pk': pk})


@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def import_test(request, pk):
    """ Test import. Use an .xlsx file to submit grades to a test

    On GET the user is presented with a file upload form.

    On POST, the submitted .xlsx file is processed by the system, registering Grade object for each grade in the excel
    file. Lines that do not have a filled in student number are ignored. Students that are not declared as part of the
    module (def:import_student_to_module) the test is in raise an import error.

    :param request: Django request
    :param pk: Test that grades should be submitted to
    :return: A redirect to the Grades module's Test view on success. Otherwise a 404 (module does not exist), 403
        (no permissions) or 400 (bad excel file or other import error)
    """
    # Check if user is either the module coordinator or teacher of this test.
    test = get_object_or_404(Test, pk=pk)
    person = Person.objects.filter(user=request.user).first()

    if not is_coordinator_or_teacher_of_test(person, test):
        raise PermissionDenied('You are not a module coordinator or teacher of this test. Please refer to the'
                               'module coordinator of this test if you think this is in error.')

    if request.method == "POST":
        form = TestGradeUploadForm(request.POST, request.FILES)

        if form.is_valid():
            title_row = form.cleaned_data.get('title_row') - 1

            sheet = request.FILES['file'].get_book_dict()
            for table in sheet:
                # Check dimensions
                if not len(sheet[table]) > title_row and len(sheet[table][0]) == 3:
                    return bad_request(request, {'message': 'The file that was uploaded was not recognised as a grade '
                                                            'excel file. Are you sure all columns are present? '
                                                            'Otherwise, download a new gradesheet and try using that '
                                                            'instead.'})
                # Identify columns
                try:
                    student_id_field = sheet[table][title_row].index('university_number')
                    grade_field = sheet[table][title_row].index('grade')
                    description_field = sheet[table][title_row].index('description')
                except ValueError:
                    return bad_request(request, {'message': 'One of the required field [student_id, grade, description]'
                                                            ' could not be found.'})

                # The current user's Person is the corrector of the grades.
                teacher = Person.objects.filter(user=request.user).first()

                # Check excel file for invalid students
                invalid_students = []
                for row in sheet[table][(title_row + 1):]:
                    if not Studying.objects.filter(person__university_number=row[0]).filter(
                            module_edition=test.module_part.module_edition_id):
                        invalid_students.append(row[0])
                # Check for invalid student numbers in the university_number column, but ignore empty fields.
                if [student for student in invalid_students if student is not '']:
                    return bad_request(request, {'message': 'Students {} are not enrolled in this module. '
                                                            'Enroll these students first before retrying.'
                                                            .format(invalid_students)})
                elif invalid_students:
                    return bad_request(request, {'message': 'There are grades or description fields in this excel sheet'
                                                            ' that do not have a student number filled in. Please'
                                                            ' check the contents of your excel file for stale values'
                                                            ' in rows.'})

                grades = []
                for row in sheet[table][(title_row + 1):]:
                    try:
                        student = Person.objects.get(university_number=row[student_id_field])
                        # check if this is not an empty line, else continue.
                        if student:
                            grades.append(make_grade(
                                student=student,
                                corrector=teacher,
                                test=test,
                                grade=row[grade_field],
                                description=row[description_field]
                            ))
                    except GradeException as e:  # Called for either: bad grade, grade out of bounds
                        return bad_request(request, {'error': e})
                save_grades(grades)  # Bulk-save grades. Also prevents a partial import of the sheet.
            return redirect('grades:test', pk)
        else:
            return bad_request(request, {'message': 'Bad POST'})
    else:
        if Test.objects.filter(pk=pk):
            form = TestGradeUploadForm()
            return render(request, 'importer/importtest.html',
                          {'test': Test.objects.get(pk=pk), 'form': form, 'pk': pk})

        else:
            return bad_request(request, {'message', 'Test does not exists'})


@login_required()
@require_http_methods(["GET"])
def export_module(request, pk):
    """ Creates an excel sheet that contains all tests against all students in the module. This sheet is compatible with
    def:import_module.

    :param request: Django request
    :param pk: Module ID
    :return: A file response containing an .xlsx file.
    """

    module_edition = get_object_or_404(ModuleEdition, pk=pk)
    person = Person.objects.filter(user=request.user).first()

    # Check if user is a module coordinator.
    if not is_coordinator_or_assistant_of_module(person, module_edition):
        raise PermissionDenied('You are not the module coordinator for this course.')

    students = Person.objects.filter(studying__module_edition=module_edition).values('university_number', 'name')
    tests = Test.objects.filter(module_part__module_edition=module_edition)

    # Pre-fill first few columns.
    table = [
                ['Module:', str(module_edition)]+['' for _ in range(len(tests))],

            ] + [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW - 4)]

    # Add the module part name and test name for each test if there is enough header room.
    if COLUMN_TITLE_ROW > 2:
        table.append(['', 'Module part >'] + [test.module_part.name for test in tests])
    if COLUMN_TITLE_ROW > 1:
        table.append(['', 'Test name >'] + [test.name for test in tests])
    if COLUMN_TITLE_ROW > 0:
        table.append(['', 'Grade between >'] + ['{} - {}'.format(test.minimum_grade, test.maximum_grade) for test in tests])

    # Add machine-readable header row.
    table.append(['university_number', 'name'] + [test.pk for test in tests])

    # pre-fill student numbers
    for student in students:
        table.append([student['university_number'], student['name']] + [None for _ in range(len(tests))])

    return excel.make_response_from_array(table,
                                          file_name='Module Grades {} {}-{}.xlsx'.format(module_edition.module.name,
                                                                                         module_edition.year,
                                                                                         module_edition.block),
                                          file_type='xlsx')


@login_required()
@require_http_methods(["GET"])
def export_module_part(request, pk):
    """ Creates an excel sheet that contains all tests that are in a course. Used mainly to download sign off excel sheets.

    :param request: Django request
    :param pk: Module part ID
    :return: A file response containing an .xlsx file.
    """

    module_part = get_object_or_404(ModulePart, pk=pk)
    module_edition = ModuleEdition.objects.get(modulepart=module_part)
    person = Person.objects.filter(user=request.user).first()

    # Check if user is a module coordinator.
    if not is_coordinator_or_teacher_of_module_part(person, module_part):
        raise PermissionDenied('You are not the module coordinator for this course.')

    students = Person.objects.filter(studying__module_edition=module_edition).values('university_number', 'name')
    tests = Test.objects.filter(module_part=module_part).values('pk', 'name', 'minimum_grade', 'maximum_grade')

    # Pre-fill first few columns.
    table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW - 2)]

    # Add the module part name and test name for each test if there is enough header room.
    if COLUMN_TITLE_ROW > 1:
        table.append(['', 'Test name >'] + [test['name'] for test in tests])
    if COLUMN_TITLE_ROW > 0:
        table.append(['', 'Grade between >'] + ['{} - {}'.format(test['minimum_grade'], test['maximum_grade']) for test in tests])

    # Add machine-readable header row.
    table.append(['university_number', 'name'] + [test['pk'] for test in tests])

    # pre-fill student numbers
    for student in students:
        table.append([student['university_number'], student['name']] + [None for _ in range(len(tests))])

    return excel.make_response_from_array(table,
                                          file_name='Sign-off sheet {} {}-{}.xlsx'.format(module_edition.module.name,
                                                                                          module_edition.year,
                                                                                          module_edition.block),
                                          file_type='xlsx')


@login_required()
@require_http_methods(["GET"])
def export_module_part_signoff(request, pk):
    """ Creates an excel sheet that contains all tests that are in a course. Used mainly to download sign off excel sheets.

    :param request: Django request
    :param pk: Module part ID
    :return: A file response containing an .xlsx file.
    """

    module_part = get_object_or_404(ModulePart, pk=pk)
    module_edition = ModuleEdition.objects.get(modulepart=module_part)
    person = Person.objects.filter(user=request.user).first()

    # Check if user is a module coordinator.
    if not is_coordinator_or_teacher_of_module_part(person, module_part):
        raise PermissionDenied('You are not the module coordinator for this course.')

    students = Person.objects.filter(studying__module_edition=module_edition).values('university_number', 'name')
    tests = Test.objects.filter(module_part=module_part, type='A').values('pk', 'name', 'minimum_grade', 'maximum_grade')

    # Pre-fill first few columns.
    table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW - 2)]

    # Add the module part name and test name for each test if there is enough header room.
    if COLUMN_TITLE_ROW > 1:
        table.append(['', 'Test name >'] + [test['name'] for test in tests])
    if COLUMN_TITLE_ROW > 0:
        table.append(['', 'Grade between >'] + ['{} - {}'.format(test['minimum_grade'], test['maximum_grade']) for test in tests])

    # Add machine-readable header row.
    table.append(['university_number', 'name'] + [test['pk'] for test in tests])

    # pre-fill student numbers
    for student in students:
        table.append([student['university_number'], student['name']] + [None for _ in range(len(tests))])

    return excel.make_response_from_array(table,
                                          file_name='Sign-off sheet {} {}-{}.xlsx'.format(module_edition.module.name,
                                                                                          module_edition.year,
                                                                                          module_edition.block),
                                          file_type='xlsx')

@login_required()
@require_http_methods(["GET"])
def export_test(request, pk):
    """ Creates an excel sheet that contains all students that may take the test. This sheet is compatible with
    def:import_test. It contains a description row, which can be used to submit feedback through.

    :param request: Django request
    :param pk: Test ID
    :return: A file response containing an .xlsx file.
    """

    test = get_object_or_404(Test, pk=pk)
    person = Person.objects.filter(user=request.user).first()

    # Check if user is either the module coordinator or teacher of this test.
    if not is_coordinator_or_teacher_of_test(person, test):
        raise PermissionDenied('Not allowed to export test.')

    students = Person.objects.filter(studying__module_edition__modulepart=test.module_part).values('university_number',
                                                                                                   'name')

    # Insert padding
    table = [
                [test.name, "", "grade between:", '{} - {}'.format(test.minimum_grade, test.maximum_grade)]
            ] + [['', '', '', ''] for _ in range(COLUMN_TITLE_ROW - 1)]

    # Insert title row
    table.append(['university_number', 'name', 'grade', 'description'])

    # Insert student numbers
    for student in students:
        table.append([student['university_number'], student['name'], '', ''])

    return excel.make_response_from_array(table, file_name='Test Grades {} {}-{}.xlsx'
                                          .format(test.name,
                                                  test.module_part.module_edition.year,
                                                  test.module_part.module_edition.block),
                                          file_type='xlsx')


def make_grade(student: Person, corrector: Person, test: Test, grade, description: str = ''):
    """ Helper function that makes Grade objects so they can be inserted in bulk with def:save_grades.
    :param student: Person object of the student.
    :param corrector: Person object of the corrector.
    :param test: Test object.
    :param grade: A float that is the grade.
    :param description: An optional description.
    :return: A grade object, or None (:param grade is empty).
    """
    if grade == '':
        return  # Field is empty, assume it does not need to be imported.
    try:
        float(grade)
    except (ValueError, TypeError):
        if test.type == 'A':
            grade = 1
        else:
            raise GradeException('\'{}\' is not a valid input for a grade (found at {}\'s grade for {}.)'
                                 .format(grade, student.name, test))  # Probably a typo, give an error.
    if test.minimum_grade > grade or grade > test.maximum_grade:
        raise GradeException(
            'Cannot register {}\'s ({}) grade for test {} because it\'s grade ({}) is outside the defined bounds '
            '({}-{}).'.format(student.name, student.university_number, test.name, grade, test.minimum_grade,
                              test.maximum_grade))

    try:
        grade_obj = Grade(
            student=student,
            teacher=corrector,
            test=test,
            grade=grade,
            time=timezone.now(),
            description=description
        )
    except Exception as e:
        raise GradeException(e)
    return grade_obj


def save_grades(grades):
    """ Helper function that saves all grades to the database.

    :param grades: List of Grade objects, which may contain None values. These are ignored.
    :return: Nothing.
    :raises: GradeException if a grade object is malformed. No grades are saved when this happens.
    """
    try:
        Grade.objects.bulk_create([grade for grade in grades if grade is not None])
    except Exception as e:
        raise GradeException('Error when saving grades to te database.')


@login_required
def workbook_student_to_module(request, pk):
    """ Creates an excel sheet that may be filled in to register students to a module. This sheet is compatible with
        def:import_student_to_module.

        :param request: Django request
        :param pk: Test ID
        :return: A file response containing an .xlsx file.
        """
    # Check if user is a module coordinator.
    module_edition = get_object_or_404(ModuleEdition, pk=pk)
    person = Person.objects.filter(user=request.user).first()
    if not is_coordinator_or_assistant_of_module(person, module_edition):
        raise PermissionDenied('You are not the module coordinator for this course.')

    # Insert column titles
    table = [['university_number', 'name', 'email', 'role']]

    return excel.make_response_from_array(table, file_name='Module import Sheet.xlsx', file_type='xlsx')


@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def import_student_to_module(request, pk):
    """
    Take .xlsx file, as produced by def:export_student_import_format and retrieve all students and metainformation from it.
    Case 1 - Known User - Add the user to the active module edition with the right study and role by making a new Studying object
    Case 2 - Unknown User - Add the student to the database by making a new Person object and proceed like Case 1
    Case 3 - Already Added User - Ignore row
    The function returns a view in which all newly added users, all users that are now added to the module edition and all users that were already in the module are shown.

    :param request: Django request
    :param pk: The module edition id
    :return: /students-module-imported.html redirect in which all fails, successes and addeds are given
    :raises: Permission denied if the user is not the Module Coordinator
    :raises: SuspiciousOperation in case of faulty file input
    """
    # Check if user is a module coordinator.
    module_edition = get_object_or_404(ModuleEdition, pk=pk)
    person = Person.objects.filter(user=request.user).first()
    if not is_coordinator_or_assistant_of_module(person, module_edition):
        raise PermissionDenied('Not allowed to upload students to module.')

    if request.method == "POST":
        student_form = ImportStudentForm(request.POST, request.FILES)
        if student_form.is_valid():
            file = request.FILES['file']
            dict = file.get_book_dict()

            # Select first page
            students_to_module = dict[list(dict.keys())[0]]

            # Check dimensions
            if not (len(students_to_module) > 1 and len(students_to_module[0]) == 4):
                return bad_request(request, {'message': 'Not all required columns [university_number, name, email, '
                                                        'role] are in the excel sheet, or no rows to import.'})

            string = ""
            emailpattern = re.compile('e[-]?mail*')
            if students_to_module[0][0].lower() == 'university_number' and students_to_module[0][
                1].lower() == 'name' and emailpattern.match(students_to_module[0][2].lower()) and \
                            students_to_module[0][3].lower() == 'role':
                context = {}
                context['created'] = []
                context['studying'] = []
                context['failed'] = []

                for i in range(1, len(students_to_module)):
                    # Sanitize number input

                    try:
                        if str(students_to_module[i][0])[0] == 's' and int(students_to_module[i][0][1:]) > 0:
                            username = str(students_to_module[i][0])
                        elif str(students_to_module[i][0])[0] == 'm' and int(students_to_module[i][0][1:]) > 0:
                            return HttpResponseBadRequest('Trying to add an employee as a student to a module.')
                        elif int(students_to_module[i][0]) > 0:
                            username = 's{}'.format(str(students_to_module[i][0]))
                        else:
                            raise ValueError
                    except ValueError:
                        return bad_request(request, {'message': '{} is not a student number.'
                                                                .format(students_to_module[i][0])})
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': students_to_module[i][2]
                        }
                    )

                    student, created = Person.objects.get_or_create(
                        university_number=str(students_to_module[i][0]),
                        defaults={
                            'user': user,
                            'name': students_to_module[i][1],
                            'email': students_to_module[i][2],
                        }
                    )
                    if created:
                        context['created'].append([student.name, student.full_id])

                    studying, created = Studying.objects.get_or_create(
                        person=student,
                        module_edition=ModuleEdition.objects.get(pk=pk),
                        defaults={
                            'role': students_to_module[i][3],
                        }
                    )
                    if created:
                        module_ed = ModuleEdition.objects.get(id=studying.module_edition.pk)
                        module = Module.objects.get(moduleedition=module_ed)
                        context['studying'].append(
                            [student.name, student.full_id, module.name, module_ed.code])  # studying.study])
                    else:
                        module_ed = ModuleEdition.objects.get(id=studying.module_edition.pk)
                        module = Module.objects.get(moduleedition=module_ed)
                        context['failed'].append(
                            [student.name, student.full_id, module.name, module_ed.code])  # studying.study])
                        context['studying'].append(
                            [student.name, student.full_id, module.name, module_ed.code])  # studying.study])
                return render(request, 'importer/students-module-imported.html', context={'context': context})
            else:
                # print(students_to_module[0][0].lower() == 'student_id')
                # print(students_to_module[0][1].lower() == 'name')
                # print(emailpattern.match(students_to_module[0][2].lower()))
                # print(startpattern.match(students_to_module[0][3].lower()))
                # print(students_to_module[0][4].lower() == 'study')
                # print(students_to_module[0][5].lower() == 'role')
                return bad_request(request, {'message': 'Not all required columns [university_number, name, email, '
                                                        'role] are in the excel sheet.'})
        else:
            raise SuspiciousOperation('Bad POST')

    else:  # if Module_ed.objects.filter(pk=pk):
        student_form = ImportStudentModule()
        return render(request, 'importer/import-module-student.html',
                      {'form': student_form, 'pk': pk, 'module_edition': ModuleEdition.objects.get(pk=pk)})



class ModuleStructureImporter(LoginRequiredMixin, View):
    """Import to bulk-create Module parts and Tests for a module.
    """

    def dispatch(self, request, *args, **kwargs):
        module_edition = get_object_or_404(ModuleEdition, pk=kwargs['pk'])
        if is_coordinator_or_assistant_of_module(Person.objects.filter(user=self.request.user).first(), module_edition):
            return super(ModuleStructureImporter, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied("You are not the module coordinator of this module.")

    def get(self, request, pk):
        module_structure_form = ImportModuleEditionStructureForm()
        return render(request, 'importer/import-module-structure.html',
                      {'form': module_structure_form, 'pk': pk, 'module_edition': ModuleEdition.objects.get(pk=pk)})

    @transaction.atomic
    def post(self, request, pk):
        module_edition = get_object_or_404(ModuleEdition, pk=pk)

        tests_in_sheet = []
        module_parts_in_sheet = []

        # Collect module parts and tests that cannot be deleted, because they contain Grades.
        old_tests = []
        old_module_parts = []

        student_form = ImportModuleEditionStructureForm(request.POST, request.FILES)
        if student_form.is_valid():
            try:
                with transaction.atomic():
                    file = request.FILES['file']
                    workbook = file.get_book_dict()

                    structure = dict()

                    for page in workbook.keys():
                        module_part, mp_created = ModulePart.objects.get_or_create(name=workbook[page][0][1], module_edition=module_edition)
                        module_parts_in_sheet.append(module_part.pk)


                        for i in range(1, len(workbook[page][0])):

                            try:

                                min_grade = float(workbook[page][2][i])
                                max_grade = float(workbook[page][3][i])

                                if min_grade == 0 and max_grade == 1:
                                    test_type = 'A'
                                else:
                                    test_type = 'E'

                                test, test_created = Test.objects.get_or_create(name=workbook[page][1][i], module_part=module_part,
                                                           defaults={'type': test_type,
                                                                     'minimum_grade': min_grade,
                                                                     'maximum_grade': max_grade})
                                test.type = test_type
                                test.minimum_grade = min_grade
                                test.maximum_grade = max_grade
                                test.save()
                                tests_in_sheet.append(test.pk)
                            except ValueError as e:
                                # If the either the minimum_grade or maximum_grade is not defined, it's not a test at
                                # all.
                                continue


                    for test in Test.objects.filter(module_part__module_edition=module_edition).exclude(
                            pk__in=tests_in_sheet):
                        if not Grade.objects.filter(test=test):
                            test.delete()
                        else:
                            old_tests.append(test)
                    for module_part in ModulePart.objects.filter(module_edition=module_edition).exclude(
                            pk__in=module_parts_in_sheet):
                        if not Grade.objects.filter(test__module_part=module_part):
                            module_part.delete()
                        else:
                            old_module_parts.append(module_part)
                    if len(old_tests) > 0 or len(old_module_parts) > 0:
                        raise IntegrityError("Some modules that should be removed have grades.")
            except IntegrityError:
                return render(request, 'importer/module_structure_import_error.html',
                              context={'old_tests': old_tests, 'old_module_parts': old_module_parts})

        else:
            return bad_request(request, {'message': 'Bad POST'})

        return redirect('module_management:module_edition_detail', pk)


def export_module_structure(request, pk):
    """ Returns an excel sheet which can be used to upload the module structure.
    :param request: Django request
    :param pk: Module edition primary key
    :return: Excel worksheet as response.
    """
    # Check if user is a module coordinator.
    module_edition = get_object_or_404(ModuleEdition, pk=pk)
    person = Person.objects.filter(user=request.user).first()
    if not is_coordinator_or_assistant_of_module(person, module_edition):
        raise PermissionDenied('You are not the module coordinator for this course.')

    # Insert column titles
    table = [
        ['Module part:', '<<example>>', '', '(Duplicate this page for each module part)'],
        ['Test:', '<<example test>>', '<<example signoff>>', ''],
        ['Min. grade', '1', '0', ''],
        ['Max. grade', '10', '1', '']
    ]

    return excel.make_response_from_array(table, file_name='Module Structure {}.xlsx'.format(module_edition), file_type='xlsx')
