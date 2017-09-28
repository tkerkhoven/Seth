from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django import forms
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.utils import timezone
from django.db.models import Q
import django_excel as excel
from xlsxwriter.utility import xl_rowcol_to_cell

from Grades.exceptions import GradeException
from Grades.models import Module_ed, Grade, Test, Person, Course
from importer.forms import GradeUploadForm, TestGradeUploadForm

# Create your views here.


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'importer/index.html'
    model = Module_ed

    def get_queryset(self):
        return Module_ed.objects.filter(module_coordinator__user=self.request.user).order_by('start')


@login_required
def import_module(request, pk):
    if not Module_ed.objects.filter(pk=pk):
        return HttpResponseNotFound('Module does not exist.')
    if not Module_ed.objects.filter(pk=pk).filter(module_coordinator__user=request.user):
        return HttpResponseForbidden('You are not the module coordinator for this course')

    if request.method == "POST":
        form = GradeUploadForm(request.POST, request.FILES)

        if form.is_valid():
            sheet = request.FILES['file'].get_book_dict()
            for table in sheet:

                test_rows = dict()

                for title_index in range(0, len(sheet[table][0])):
                    if sheet[table][0][title_index] == '':
                        continue
                    if str(sheet[table][0][title_index]).lower() == 'student_id':
                        student_id_field = title_index
                    else:
                        if Test.objects.filter(
                                pk=sheet[table][0][title_index]
                        ).filter(course_id__module_ed=pk):
                            test_rows[title_index] = sheet[table][0][title_index]
                        else:
                            return HttpResponseBadRequest('Attempt to register grade for, amongst possible other tests,'
                                                          ' test: {} (interpreted from sheet coordinates {}), which is '
                                                          'not part of this module. (Are you sure this test ID is '
                                                          'correct and therefore part of your module?)'
                                                          .format(sheet[table][0][title_index],
                                                                  xl_rowcol_to_cell(0, title_index)))
                if student_id_field is None:
                    return HttpResponseBadRequest('excel file misses required header: \"student_id\"')

                grades = []
                for row in sheet[table][1:]:
                    for test_column in test_rows.keys():
                        try:
                            if not Person.objects.filter(person_id=row[student_id_field]):
                                return HttpResponseBadRequest(
                                    'Student {} does not exist. Add this user first before retrying.'.format(
                                        row[student_id_field]))
                            if not Test.objects.filter(pk=sheet[table][0][test_column]):
                                return HttpResponseBadRequest(
                                    'Test with id {} does not exist in the database. Did you change the header field '
                                    'of the spreadsheet?'.format(sheet[table][0][test_column])
                                )
                            grades.append(make_grade(
                                student=Person.objects.filter(person_id=row[student_id_field])[0],
                                corrector=Person.objects.get(user=request.user),
                                test=Test.objects.get(pk=sheet[table][0][test_column]),
                                grade=row[test_column]
                            ))
                        except GradeException as e:
                            return HttpResponseBadRequest(e)
                save_grades(grades)
            return redirect('grades:gradebook', pk)
        else:
            return HttpResponseBadRequest()
    else:
        if Module_ed.objects.filter(pk=pk):
            form = GradeUploadForm()
            return render(request, 'importer/importmodule.html', {'form': form, 'pk': pk})

        else:
            return HttpResponseBadRequest()


@login_required
def import_test(request, pk):
    if not Test.objects.filter(pk=pk):
        return HttpResponseNotFound('Test does not exist.')
    if not Test.objects.filter(
                    Q(course_id__teachers__user=request.user) | Q(course_id__module_ed__module_coordinator__user=request.user)
    ).filter(pk=pk):
        return HttpResponseForbidden('Not allowed to alter test')

    if request.method == "POST":
        form = TestGradeUploadForm(request.POST, request.FILES)

        if form.is_valid():

            sheet = request.FILES['file'].get_book_dict()
            for table in sheet:

                try:
                    student_id_field = sheet[table][0].index('student_id')
                    grade_field = sheet[table][0].index('grade')
                    description_field = sheet[table][0].index('description')
                except ValueError:
                    return HttpResponseBadRequest()

                grades = []
                for row in sheet[table][1:]:
                    if not Person.objects.filter(person_id=row[student_id_field]):
                        return HttpResponseBadRequest('Student {} does not exist. Add this user first before retrying.'.format(row[student_id_field]))
                    try:
                        grades.append(make_grade(
                            student=Person.objects.filter(person_id=row[student_id_field])[0],
                            corrector=Person.objects.get(user=request.user),
                            test=Test.objects.get(pk=pk),
                            grade=row[grade_field],
                            description=row[description_field]
                        ))
                    except GradeException as e:
                        return HttpResponseBadRequest(e)
                save_grades(grades)
            return redirect('grades:test', pk)
        else:
            return HttpResponseBadRequest('Bad POST')
    else:
        if Test.objects.filter(pk=pk):
            form = TestGradeUploadForm()
            return render(request, 'importer/importtest.html', {'test': Test.objects.get(pk=pk), 'form': form, 'pk': pk})

        else:
            return HttpResponseBadRequest('Test does not exist')


@login_required()
def export_module(request, pk):

    if not Module_ed.objects.filter(pk=pk).filter(module_coordinator__user=request.user):
        return HttpResponseForbidden('You are not the module coordinator for this course.')

    module = Module_ed.objects.get(pk=pk)
    students = Person.objects.filter(studying__module_id=module)
    tests = Test.objects.filter(course_id__module_ed=module)

    table = [['student_id']+[test.pk for test in tests]]

    for student in students:
        table.append([student.person_id] + [None for _ in range(len(tests))])

    return excel.make_response_from_array(table, 'xlsx')


@login_required()
def export_test(request, pk):
    if not Test.objects.filter(
                    Q(course_id__teachers__user=request.user) |
                    Q(course_id__module_ed__module_coordinator__user=request.user)
    ).filter(pk=pk):
        return HttpResponseForbidden('Not allowed to export test.')
    test = Test.objects.get(pk=pk)
    students = Person.objects.filter(studying__module_id__courses=test.course_id)

    table = [['student_id', 'grade', 'description']]

    for student in students:
        table.append([student.person_id, '', ''])

    return excel.make_response_from_array(table, 'xlsx')


def make_grade(student: Person, corrector: Person, test: Test, grade: float, description: str = ''):
    if grade == '':
        return  # Field is empty, assume it does not need to be imported.

    try:
        float(grade)
    except ValueError:
        raise GradeException('\'{}\' is not a valid input for a grade (found at {}\'s grade for {}.)'
                             .format(grade, student, test))  # Probably a typo, give an error.
    if test.minimum_grade > grade or grade > test.maximum_grade:
        raise GradeException('Cannot register {}\'s ({}) grade for test {} because it\'s grade ({}) is outside the defined bounds '
                             '({}-{}).'.format(student.name, student.id_prefix + student.person_id, test.name, grade, test.minimum_grade, test.maximum_grade))

    try:
        grade_obj = Grade(
            student_id=student,
            teacher_id=corrector,
            test_id=test,
            grade=grade,
            time=timezone.now(),
            description=description
        )
    except Exception as e:
        raise GradeException(e)
    return grade_obj


def save_grades(grades: [Grade]):
    try:
        Grade.objects.bulk_create([grade for grade in grades if grade is not None])
    except:
        raise GradeException('Error when trying to save the grades to the database.')

