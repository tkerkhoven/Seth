from django.contrib import admin

# Register your models here.
from Grades.models import *

class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ['person', 'module', 'mc_assistant']

admin.site.register(Coordinator, CoordinatorAdmin)

class GradeAdmin(admin.ModelAdmin):
    list_display = ('test_id', 'time', 'student_id', 'grade')
    list_filter = ['test_id', 'time', 'student_id', 'grade']

admin.site.register(Grade, GradeAdmin)

for object in [Person, Study, Studying, Module, Module_ed, Criterion, Course, Test]:
    admin.site.register(object)

