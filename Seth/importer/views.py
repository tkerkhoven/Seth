from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.views import generic
from django.utils import timezone
from django.db.models import Q
from xlsxwriter.utility import xl_rowcol_to_cell
import re
from django.http import HttpResponse

from Grades.models import Module_ed, Grade, Test, Person, Studying, Module, Study

# Create your views here.
from importer.forms import GradeUploadForm, TestGradeUploadForm, ImportStudentForm, ImportStudentModule


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
                            return HttpResponseBadRequest(
                                'Attempt to register grade for, amongst possible other tests, test: {} (interpreted from sheet coordinates {}), which is not part of this module. (Are you sure this test ID is correct and therefore part of your module?)'.format(
                                    sheet[table][0][title_index], xl_rowcol_to_cell(0, title_index)))
                if student_id_field is None:
                    return HttpResponseBadRequest('excel file misses required header: \"student_id\"')

                print('Saving grades')
                grades = []
                for row in sheet[table][1:]:
                    for test_column in test_rows.keys():
                        grades.append(Grade(
                            student_id=Person.objects.filter(person_id=row[student_id_field])[0],
                            teacher_id=Person.objects.filter(user=request.user.pk)[0],
                            # TODO: Research proper query when roles are removed from model
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

                for row in sheet[table][1:]:
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
            return render(request, 'importer/importtest.html',
                          {'test': Test.objects.get(pk=pk), 'form': form, 'pk': pk})

        else:
            return HttpResponseBadRequest('Test does not exist')


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
