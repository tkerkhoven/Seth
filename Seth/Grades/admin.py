from django.contrib import admin

# Register your models here.
from Grades.models import *


class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ['person', 'module', 'is_assistant']


admin.site.register(Coordinator, CoordinatorAdmin)


class GradeAdmin(admin.ModelAdmin):
    list_display = ('test', 'time', 'student', 'grade')
    list_filter = ['test', 'time', 'student', 'grade']


admin.site.register(Grade, GradeAdmin)


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('person', 'module_part', 'role')
    list_filter = ['person', 'module_part', 'role']


admin.site.register(Teacher, TeacherAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'university_number', 'start', 'end', 'user')
    list_filter = ['university_number']


admin.site.register(Person, PersonAdmin)


for object in [Study, Studying, Module, ModuleEdition, Criterion, ModulePart, Test]:
    admin.site.register(object)
