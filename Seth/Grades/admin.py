from django.contrib import admin

# Register your models here.
from Grades.models import *


class GradeAdmin(admin.ModelAdmin):
    list_display = ('test_id', 'time', 'student_id', 'grade')
    list_filter = ['test_id', 'time', 'student_id', 'grade']

admin.site.register(Grade, GradeAdmin)

for object in [Study, Studying, Module, Module_ed, Criterion, Course, Test, Student, Teacher, Advisor]:
    admin.site.register(object)

