from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django import forms
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.utils import timezone
from django.db.models import Q
import django_excel as excel
from xlsxwriter.utility import xl_rowcol_to_cell

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

    if not Module_ed.objects.filter(pk=pk).filter(module_coordinator__user=request.user):
        return HttpResponseForbidden()

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
                            return HttpResponseBadRequest('Attempt to register grade for, amongst possible other tests, test: {} (interpreted from sheet coordinates {}), which is not part of this module. (Are you sure this test ID is correct and therefore part of your module?)'.format(sheet[table][0][title_index], xl_rowcol_to_cell(0, title_index)))
                if student_id_field is None:
                    return HttpResponseBadRequest('excel file misses required header: \"student_id\"')

                print('Saving grades')
                grades = []
                for row in sheet[table][1:]:
                    for test_column in test_rows.keys():
                        grades.append(Grade(
                            student_id=Person.objects.filter(person_id=row[student_id_field])[0],
                            teacher_id=Person.objects.filter(user=request.user.pk)[0], # TODO: Research proper query when roles are removed from model
                            test_id=Test.objects.get(pk=test_rows[test_column]),
                            grade=row[test_column],
                            time=timezone.now()
                        ))
                Grade.objects.bulk_create(grades)

            # request.FILES['file'].save_to_database(Grade,test_func,
            #         ['student_id', 'teacher_id', 'test_id', 'grade', 'description', 'time']
            # )
            return redirect('import_index')
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

                for row in sheet[table][1:]:
                    if not Person.objects.filter(person_id=row[student_id_field]):
                        return HttpResponseBadRequest('Student {} does not exist. Add this user first before retrying.'.format(row[student_id_field]))
                    if row[grade_field] == '':
                        continue
                    Grade(
                        student_id=Person.objects.filter(person_id=row[student_id_field])[0],
                        teacher_id=Person.objects.filter(user=request.user.pk)[0],
                        test_id=Test.objects.get(pk=pk),
                        grade=row[grade_field],
                        time=timezone.now(),
                        description=row[description_field]
                    ).save()
            return redirect('import_index')
        else:
            return HttpResponseBadRequest('Bad POST')
    else:
        if Test.objects.filter(pk=pk):
            form = TestGradeUploadForm()
            return render(request, 'importer/importtest.html', {'test': Test.objects.get(pk=pk), 'form': form, 'pk': pk})

        else:
            return HttpResponseBadRequest('Test does not exist')


def export_module(request, pk):
    module = Module_ed.objects.get(pk=pk)
    students = Person.objects.filter(studying__module_id=module)
    tests = Test.objects.filter(course_id__module_ed=module)

    table = [['student_id']+[test.pk for test in tests]]

    for student in students:
        table.append([student.person_id] + [None for _ in range(len(tests))])

    return excel.make_response_from_array(table, 'xlsx')


def export_test(request, pk):
    test = Test.objects.get(pk=pk)
    students = Person.objects.filter(studying__module_id__courses=test.course_id)

    table = [['student_id', 'grade', 'description']]

    for student in students:
        table.append([student.person_id, '', ''])

    return excel.make_response_from_array(table, 'xlsx')
