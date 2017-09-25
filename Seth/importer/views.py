from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django import forms
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.utils import timezone

from Grades.models import Module_ed, Grade, Test, Person

# Create your views here.
from importer.forms import GradeUploadForm


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
        form = GradeUploadForm(pk, request.POST, request.FILES)

        def test_func(row):
            student = Person.objects.filter(person_id=row[0])[0]
            row[0] = student

            teacher = Person.objects.filter(user=request.user.pk)[0]
            row[1] = teacher

            test = Test.objects.get(pk=form.cleaned_data['test'].pk)
            row[2] = test

            row[5] = timezone.now()

            print(row)
            return row

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
                        test_id=Test.objects.get(pk=form.cleaned_data['test'].pk),
                        grade=row[grade_field],
                        time=timezone.now(),
                        description=row[description_field]
                    ).save()

            # request.FILES['file'].save_to_database(Grade,test_func,
            #         ['student_id', 'teacher_id', 'test_id', 'grade', 'description', 'time']
            # )
            return redirect('import_index')
        else:
            return HttpResponseBadRequest()
    else:
        if Module_ed.objects.filter(pk=pk):
            form = GradeUploadForm(pk)
            return render(request, 'importer/importmodule.html', {'form': form, 'pk': pk})

        else:
            return HttpResponseBadRequest()


