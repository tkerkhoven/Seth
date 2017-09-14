from django.contrib import admin

# Register your models here.
from Grades.models import *

for object in [Person, Studying, Module, Module_ed, Criterion, Course, Test, Grade, Advisor]:
    admin.site.register(object)
