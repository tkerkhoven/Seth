from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, SuspiciousOperation
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

import re

from Grades.exceptions import GradeException
from Grades.models import ModuleEdition, Grade, Test, Person, ModulePart, Studying, Module, Study
from importer.forms import GradeUploadForm, TestGradeUploadForm, ImportStudentForm, ImportStudentModule


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

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        person = Person.objects.filter(user=request.user).first()
        if is_coordinator_or_assistant(person):
            return render(request, 'importer/mcindex.html', {
                'module_ed_list': ModuleEdition.objects.filter(coordinator__person__user=self.request.user).order_by(
                    'start')})
        elif is_teacher(person):
            return render(request, 'importer/teacherindex.html',
                          {'course_list': ModulePart.objects.filter(teacher__person__user=self.request.user).order_by(
                              'module_edition__start')})

        raise PermissionDenied('Only module coordinators or teachers can view this page.')


    # def get_queryset(self):
    #     return ModuleEdition.objects.filter(coordinators__person__user=self.request.user).order_by('start')


COLUMN_TITLE_ROW = 5  # title-row, zero-indexed, that contains the title for the grade sheet rows.


@login_required
@require_http_methods(["GET", "POST"])
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
    if not ModuleEdition.objects.filter(pk=pk):
        raise Http404('Module does not exist.')
    if not is_coordinator_or_assistant(person):
        raise PermissionDenied('You are not the module coordinator for this course')

    if request.method == "POST":
        form = GradeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            sheet = request.FILES['file'].get_book_dict()
            for table in sheet:

                test_rows = dict()

                university_number_field = None

                # Detect university_number and test columns
                for title_index in range(0, len(sheet[table][COLUMN_TITLE_ROW])):
                    # Ignore empty column titles
                    if sheet[table][COLUMN_TITLE_ROW][title_index] == '':
                        continue
                    # This is the university number column
                    if str(sheet[table][COLUMN_TITLE_ROW][title_index]).lower() == 'student_id':
                        university_number_field = title_index
                    else:
                        # Attempt to find a Test

                        # search by ID
                        if Test.objects.filter(
                                pk=sheet[table][COLUMN_TITLE_ROW][title_index]
                        ).filter(module_part__module_edition=pk):
                            test_rows[title_index] = sheet[table][COLUMN_TITLE_ROW][title_index]  # pk of Test

                        # search by name
                        elif Test.objects.filter(
                                name=sheet[table][COLUMN_TITLE_ROW][title_index]
                        ).filter(module_part__module_edition=pk):
                            test_rows[title_index] = Test.objects.filter(
                                name=sheet[table][COLUMN_TITLE_ROW][title_index]
                            ).filter(module_part__module_edition=pk)[0].pk  # pk of Test

                        # Attempt to ignore test altogether.
                        else:
                            pass

                if university_number_field is None:
                    raise SuspiciousOperation('excel file misses required header: \"student_id\"')

                # The current user's Person is the corrector of the grades.
                teacher = Person.objects.get(user=request.user)

                grades = []

                # Retrieve Test object beforehand to speed up Grade creation
                tests = dict()
                for test_column in test_rows.keys():
                    tests[test_column] = Test.objects.get(pk=sheet[table][COLUMN_TITLE_ROW][test_column])

                # Check excel file for invalid students
                invalid_students = []
                for row in sheet[table][(COLUMN_TITLE_ROW + 1):]:
                    if not Studying.objects.filter(person__university_number=row[university_number_field]).filter(
                            module_edition=pk):
                        invalid_students.append(row[university_number_field])
                # Check for invalid student numbers in the university_number column, but ignore empty fields.
                if [student for student in invalid_students if student is not '']:
                    raise SuspiciousOperation(
                        'Students {} are not enrolled in this module. '
                        'Enroll these students first before retrying.'.format(invalid_students))

                # Make Grades
                for row in sheet[table][(COLUMN_TITLE_ROW + 1):]:  # Walk horizontally over table
                    student = Person.objects.filter(university_number=row[university_number_field])[0]
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
            return redirect('grades:gradebook', pk)
        else:
            raise SuspiciousOperation('The file that was uploaded was not recognised as a grade excel file. Are you'
                                      'sure the file is an .xlsx file? Otherwise, download a new gradesheet and try'
                                      'using that instead.')
    else:  # GET request
        form = GradeUploadForm()
        return render(request, 'importer/importmodule.html', {'form': form, 'pk': pk})


@login_required
@require_http_methods(["GET", "POST"])
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

            sheet = request.FILES['file'].get_book_dict()
            for table in sheet:
                # Identify columns
                try:
                    student_id_field = sheet[table][COLUMN_TITLE_ROW].index('student_id')
                    grade_field = sheet[table][COLUMN_TITLE_ROW].index('grade')
                    description_field = sheet[table][COLUMN_TITLE_ROW].index('description')
                except ValueError:
                    raise SuspiciousOperation('One of the required fields [student_id, grade, description] could'
                                              ' not be found.')

                # The current user's Person is the corrector of the grades.
                teacher = Person.objects.get(user=request.user)

                # Check excel file for invalid students
                invalid_students = []
                for row in sheet[table][(COLUMN_TITLE_ROW + 1):]:
                    if not Studying.objects.filter(module_id__courses__test__exact=pk,
                                                   student_id__person_id=row[student_id_field]):
                        if not row[student_id_field] == '':
                            invalid_students.append(row[student_id_field])
                # Check for invalid student numbers in the university_number column, but ignore empty fields.
                if [student for student in invalid_students if student is not '']:
                    raise SuspiciousOperation(
                        'Students {} are not enrolled in this module. '
                        'Enroll these students first before retrying.'.format(invalid_students))

                grades = []
                for row in sheet[table][(COLUMN_TITLE_ROW + 1):]:
                    try:
                        student = Person.objects.get(person_id=row[student_id_field])
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
                        return HttpResponseBadRequest(e)
                save_grades(grades)  # Bulk-save grades. Also prevents a partial import of the sheet.
            return redirect('grades:test', pk)
        else:
            raise SuspiciousOperation('Bad POST')
    else:
        if Test.objects.filter(pk=pk):
            form = TestGradeUploadForm()
            return render(request, 'importer/importtest.html',
                          {'test': Test.objects.get(pk=pk), 'form': form, 'pk': pk})

        else:
            raise SuspiciousOperation('Test does not exist')


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

    students = Person.objects.filter(studying__module_edition=module_edition)
    tests = Test.objects.filter(module_part__module_edition=module_edition)

    # Pre-fill first few columns.
    table = [['' for _ in range(len(tests) + 1)] for _ in range(COLUMN_TITLE_ROW - 2)]

    # Add the module part name and test name for each test if there is enough header room.
    if COLUMN_TITLE_ROW > 1:
        table.append(['Module part >'] + [test.module_part.name for test in tests])
    if COLUMN_TITLE_ROW > 0:
        table.append(['Test name >'] + [test.name for test in tests])

    # Add machine-readable header row.
    table.append(['student_id'] + [test.pk for test in tests])

    # pre-fill student numbers
    for student in students:
        table.append([student.university_number] + [None for _ in range(len(tests))])

    return excel.make_response_from_array(table,
                                          file_name='Module Grades {} {}-{}.xlsx'.format(module_edition.module.name,
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

    students = Person.objects.filter(studying__module_edition__modulepart=test.module_part)

    # Insert padding
    table = [['', '', ''] for _ in range(COLUMN_TITLE_ROW)]

    # Insert title row
    table.append(['student_id', 'grade', 'description'])

    # Insert student numbers
    for student in students:
        table.append([student.university_number, '', ''])

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
    except ValueError:
        raise GradeException('\'{}\' is not a valid input for a grade (found at {}\'s grade for {}.)'
                             .format(grade, student, test))  # Probably a typo, give an error.
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
@require_http_methods(["GET", "POST"])
def import_student(request):
    person = Person.objects.filter(user=request.user).first()

    if not is_coordinator_or_assistant(person):
        raise PermissionDenied('Not allowed to add students if not a module coordinator')

    if request.method == "POST":
        student_form = ImportStudentForm(request.POST, request.FILES)

        if student_form.is_valid():
            file = request.FILES['file']
            dict = file.get_book_dict()
            new_students = dict[list(dict.keys())[0]]
            string = ""
            if new_students[0][0].lower() == 'name' and new_students[0][1].lower() == 's-number' and new_students[0][
                2].lower() == 'starting date (dd/mm/yy)':
                for i in range(1, len(new_students)):
                    new_student = Person(name=new_students[i][0], university_number=new_students[i][1],
                                         start=new_students[i][2])
                    new_student.save()
                    string += "Student added:<br>"
                    string += "Name: %s<br>Number: %d<br>Start:%s<br>" % (
                        new_students[i][0], new_students[i][1], new_students[i][2])
                    string += "-----------------------------------------<br>"
                return HttpResponse(string)
            else:
                raise SuspiciousOperation("Incorrect xls-format")

        else:
            raise SuspiciousOperation('Bad POST')
    else:
        # if Module_ed.objects.filter(pk=pk):
        student_form = ImportStudentForm()
        return render(request, 'importer/import-new-student.html',
                      {'form': student_form})

        # else:
        # return HttpResponseBadRequest('You are not an Admin')


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
    table = [['student_id', 'name', 'email', 'start date', 'study', 'role']]

    print("foo")

    return excel.make_response_from_array(table, file_name='Module import Sheet.xlsx', file_type='xlsx')


@login_required
@require_http_methods(["GET", "POST"])
def import_student_to_module(request, pk):
    # Check if user is a module coordinator.
    module_edition = get_object_or_404(ModuleEdition, pk=pk)
    person = Person.objects.filter(user=request.user).first()
    if not is_coordinator_or_assistant_of_module(person, module_edition):
        raise PermissionDenied('Not allowed to upload students to module.')

    if request.method == "POST":
        student_form = ImportStudentForm(request.POST, request.FILES)
        print('hello')
        if student_form.is_valid():
            file = request.FILES['file']
            dict = file.get_book_dict()
            students_to_module = dict[list(dict.keys())[0]]
            string = ""
            startpattern = re.compile('start*')
            emailpattern = re.compile('email*')
            if students_to_module[0][0].lower() == 'student_id' and students_to_module[0][
                1].lower() == 'name' and emailpattern.match(students_to_module[0][2].lower()) and startpattern.match(
                    students_to_module[0][3].lower()) and students_to_module[0][4].lower() == 'study' and \
                            students_to_module[0][5].lower() == 'role':
                context = {}
                context['created'] = []
                context['studying'] = []
                context['failed'] = []

                for i in range(1, len(students_to_module)):
                    student, created = Person.objects.get_or_create(
                        university_number=str(students_to_module[i][0]),
                        defaults={
                            'name': students_to_module[i][1],
                            'email': students_to_module[i][2],
                            'start': students_to_module[i][3],
                        }
                    )
                    if created:
                        context['created'].append([student.name, student.full_id])
                    studying, created = Studying.objects.get_or_create(
                        person=student,
                        module_edition=ModuleEdition.objects.get(pk=pk),
                        study=Study.objects.get(abbreviation=students_to_module[i][4]),
                        defaults={
                            'role': students_to_module[i][5],
                        }
                    )
                    if created:
                        module_ed = ModuleEdition.objects.get(id=studying.module_edition.pk)
                        module = Module.objects.get(moduleedition=module_ed)
                        context['studying'].append(
                            [student.name, student.full_id, module.name, module_ed.code, studying.study])
                    else:
                        module_ed = ModuleEdition.objects.get(id=studying.module_edition.pk)
                        module = Module.objects.get(moduleedition=module_ed)
                        context['failed'].append(
                            [student.name, student.full_id, module.name, module_ed.code, studying.study])
                        context['studying'].append(
                            [student.name, student.full_id, module.name, module_ed.code, studying.study])
                print(context)
                return render(request, 'importer/students-module-imported.html', context={'context': context})
            else:
                raise SuspiciousOperation("Incorrect xls-format")
        else:
            raise SuspiciousOperation('Bad POST')

    else:  # if Module_ed.objects.filter(pk=pk):
        student_form = ImportStudentModule()
        return render(request, 'importer/import-module-student.html',
                      {'form': student_form, 'pk': pk})

# else:
# return HttpResponseBadRequest('You are not an Admin')
