from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.utils import timezone
from django.db.models import Q
import django_excel as excel
from xlsxwriter.utility import xl_rowcol_to_cell

import re

from Grades.exceptions import GradeException
from Grades.models import Module_ed, Grade, Test, Person, Course, Studying, Module
from importer.forms import GradeUploadForm, TestGradeUploadForm, ImportStudentForm, ImportStudentModule


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
        print('valid form')
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
                            return HttpResponseBadRequest(
                                'Attempt to register grade for, amongst possible other tests, test: {} (interpreted from sheet coordinates {}), which is not part of this module. (Are you sure this test ID is correct and therefore part of your module?)'.format(
                                    sheet[table][0][title_index], xl_rowcol_to_cell(0, title_index)))
                if student_id_field is None:
                    return HttpResponseBadRequest('excel file misses required header: \"student_id\"')

                teacher = Person.objects.get(user=request.user)

                grades = []

                tests = dict()
                for test_column in test_rows.keys():
                    tests[test_column] = Test.objects.get(pk=sheet[table][0][test_column])

                # check for invalid students
                for row in sheet[table][1:]:
                    if not Person.objects.filter(person_id=row[student_id_field]):
                        return HttpResponseBadRequest(
                            'Student {} does not exist. Add this user first before retrying.'.format(
                                row[student_id_field]))


                for row in sheet[table][1:]:
                    student = Person.objects.filter(person_id=row[student_id_field])[0]
                    for test_column in test_rows.keys():
                        try:
                            grades.append(make_grade(
                                student=student,
                                corrector=teacher,
                                test=tests[test_column],
                                grade=row[test_column]
                            ))
                        except GradeException as e:
                            return HttpResponseBadRequest(e)
                save_grades(grades)
            return redirect('grades:gradebook', pk)
        else:
            return HttpResponseBadRequest('Invalid file')
    else:
        if Module_ed.objects.filter(pk=pk):
            form = GradeUploadForm()
            return render(request, 'importer/importmodule.html', {'form': form, 'pk': pk})

        else:
            return HttpResponseBadRequest('This module does not exist.')


@login_required
def import_test(request, pk):
    if not Test.objects.filter(pk=pk):
        return HttpResponseNotFound('Test does not exist.')
    if not Test.objects.filter(
                    Q(course_id__teachers__user=request.user) | Q(
                course_id__module_ed__module_coordinator__user=request.user)
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

                teacher = Person.objects.get(user=request.user)

                grades = []
                for row in sheet[table][1:]:
                    if not Person.objects.filter(person_id=row[student_id_field]):
                        return HttpResponseBadRequest('Student {} does not exist. Add this user first before retrying.'.format(row[student_id_field]))
                    try:
                        grades.append(make_grade(
                            student=Person.objects.filter(person_id=row[student_id_field])[0],
                            corrector=teacher,
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
            return render(request, 'importer/importtest.html',
                          {'test': Test.objects.get(pk=pk), 'form': form, 'pk': pk})

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


def save_grades(grades):
    try:
        Grade.objects.bulk_create([grade for grade in grades if grade is not None])
    except:
        raise GradeException('Error when trying to save the grades to the database.')

@login_required
def import_student(request):
    # if not Module_ed.objects.filter(              # ToDo: Check if User is actually Admin
    #         Q(module_coordinator__user=request.user)
    # ).filter(pk=pk):
    #     return HttpResponseForbidden('Not allowed to alter test')

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
                    new_student = Person(name=new_students[i][0], id_prefix='s', person_id=new_students[i][1],
                                         start=new_students[i][2])
                    new_student.save()
                    string += "Student added:<br>"
                    string += "Name: %s<br>Number: %d<br>Start:%s<br>" % (
                        new_students[i][0], new_students[i][1], new_students[i][2])
                    string += "-----------------------------------------<br>"
                return HttpResponse(string)
            else:
                return HttpResponseBadRequest("Incorrect xls-format")


        else:
            return HttpResponseBadRequest('Bad POST')
    else:
        # if Module_ed.objects.filter(pk=pk):
        student_form = ImportStudentForm()
        return render(request, 'importer/import-new-student.html',
                      {'form': student_form})

        # else:
        # return HttpResponseBadRequest('You are not an Admin')


@login_required
def import_student_to_module(request, pk):
    # if not Module_ed.objects.filter(              # ToDo: Check if User is actually Admin
    #         Q(module_coordinator__user=request.user)
    # ).filter(pk=pk):
    #     return HttpResponseForbidden('Not allowed to alter test')

    if request.method == "POST":
        student_form = ImportStudentForm(request.POST, request.FILES)
        print('hello')
        if student_form.is_valid():
            file = request.FILES['file']
            dict = file.get_book_dict()
            students_to_module = dict[list(dict.keys())[0]]
            string = ""
            startpattern = re.compile('start*')
            if students_to_module[0][0].lower() == 's-number' and students_to_module[0][1].lower() == 'name' and \
                    startpattern.match(students_to_module[0][
                                           2].lower()) and students_to_module[0][3].lower() == 'study' and \
                            students_to_module[0][4].lower() == 'role':
                context = {}
                context['created'] = []
                context['studying'] = []
                context['failed'] = []

                for i in range(1, len(students_to_module)):
                    student, created = Person.objects.get_or_create(
                        id_prefix='s',
                        person_id=str(students_to_module[i][0]),
                        defaults={
                            'name': students_to_module[i][1],
                            'start': students_to_module[i][2],
                        }
                    )
                    if created:
                        context['created'].append([student.name, student.full_id])
                    studying, created = Studying.objects.get_or_create(
                        student_id=student,
                        module_id_id=pk,
                        study_id=students_to_module[i][3],
                        defaults={
                            'role': students_to_module[i][4],
                        }
                    )
                    if created:
                        module_ed = Module_ed.objects.get(id=studying.module_id.pk)
                        module = Module.objects.get(module_code=module_ed.module_id)
                        context['studying'].append(
                            [student.name, student.full_id, module.name, module_ed.module_code, studying.study])
                    else:
                        module_ed = Module_ed.objects.get(id=studying.module_id.pk)
                        module = Module.objects.get(module_code=module_ed.module_id)
                        context['failed'].append(
                            [student.name, student.full_id, module.name, module_ed.module_code, studying.study])
                        context['studying'].append(
                            [student.name, student.full_id, module.name, module_ed.module_code, studying.study])
                print(context)
                return render(request, 'importer/students-module-imported.html', context={'context': context})
            else:
                return HttpResponseBadRequest("Incorrect xls-format")
        else:
            return HttpResponseBadRequest('Bad POST')

    else:  # if Module_ed.objects.filter(pk=pk):
        student_form = ImportStudentModule()
        return render(request, 'importer/import-module-student.html',
                      {'form': student_form, 'pk': pk})

# else:
# return HttpResponseBadRequest('You are not an Admin')
