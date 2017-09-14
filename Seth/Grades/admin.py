from django.contrib import admin

# Register your models here.
from Grades.models import *

for object in [Study, Studying, Module, Module_ed, Criterion, Course, Test, Grade, Student, Teacher, Advisor]:
    admin.site.register(object)
