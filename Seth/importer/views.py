from django.contrib.sessions.models import Session
from django import forms
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.utils import timezone

from Grades.models import Module_ed, Grade, Test, Person

# Create your views here.
from importer.forms import GradeUploadForm


class IndexView(generic.ListView):
    template_name = 'importer/index.html'
    model = Module_ed

    def get_queryset(self):
        return Module_ed.objects.order_by('start')

# class ImportModuleView(generic.FormView):
#     template_name = 'importer/importmodule.html'
#     form_class = UploadFileForm
#
#     def form_valid(self, form):
#         form.save_book_to_database(
#             models=[Grade],
#             initializers=[None],
#             mapdicts=[
#                 ['student_id', 'teacher_id', 'test_id', 'grade', 'description', 'time']]
#         )
#         return super(ImportModuleView, self).form_valid(form)



def import_module(request, pk):
    if request.method == "POST":
        form = GradeUploadForm(request.POST,
                              request.FILES)

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
        form = GradeUploadForm()

        # Does not work
        #form.test = forms.ModelChoiceField(queryset=Test.objects.filter(course_id__module_ed__pk=pk), label='Test to register grades for', to_field_name="pk")

        return render(request, 'importer/importmodule.html', {'form': form, 'pk': pk})