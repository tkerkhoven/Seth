from django.contrib import admin

# Register your models here.
from Grades.models import *


# Inline classes
class CoordinatorInline(admin.TabularInline):
    model = Coordinator
    extra = 1


class TeacherInline(admin.TabularInline):
    model = Teacher
    extra = 1


# Admin Views
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'university_number', 'email', 'start', 'end', 'user')
    list_filter = ['university_number']
    inlines = (CoordinatorInline, TeacherInline)


class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ['person', 'module_edition', 'is_assistant']


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('person', 'module_part', 'role')
    list_filter = ['person', 'module_part', 'role']


class ModuleEditionAdmin(admin.ModelAdmin):
    inlines = (CoordinatorInline,)


class ModulePartAdmin(admin.ModelAdmin):
    inlines = (TeacherInline,)


class GradeAdmin(admin.ModelAdmin):
    list_display = ('test', 'time', 'student', 'grade')
    list_filter = ['test', 'time', 'student', 'grade']


# Registrations
admin.site.register(Person, PersonAdmin)
admin.site.register(Coordinator, CoordinatorAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(ModuleEdition, ModuleEditionAdmin)
admin.site.register(ModulePart, ModulePartAdmin)
admin.site.register(Grade, GradeAdmin)

for grade_object in [Study, Studying, Module, Criterion, Test]:
    admin.site.register(grade_object)
