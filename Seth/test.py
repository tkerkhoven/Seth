from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.db import models

from Grades.models import Module, Person, Study, ModuleEdition, ModulePart, Studying, Test, Grade, Teacher, Coordinator
from Seth.settings import LOGIN_URL
from module_management.views import IndexView, ModuleView, ModuleEdView


class ModuleManagementIndexTests(TestCase):
    module_assigned = None
    module_unassigned = None
    module_ed_assigned = None
    module_ed_unassigned = None

    coordinator = None
    coordinator_assistant = None
    adviser = None
    teacher = None
    teaching_assistant = None
    student = None

    def setUp(self):
        # Setup User objects
        User.objects.get_or_create(
            username=u'CoordinatorTest',
            password=u'blablabla'
        )
        User.objects.get_or_create(
            username=u'CoordinatorAssistantTest',
            password=u'blablabla'
        )
        User.objects.get_or_create(
            username=u'AdviserTest',
            password=u'blablabla'
        )
        User.objects.get_or_create(
            username=u'TeacherTest',
            password=u'blablabla'
        )
        User.objects.get_or_create(
            username=u'TeachingAssistantTest',
            password=u'blablabla'
        )
        User.objects.get_or_create(
            username=u'StudentTest',
            password=u'blablabla'
        )
        # Setup Person objects
        self.coordinator = Person.objects.get_or_create(
            name='Coordinator Test',
            user='CoordinatorTest',
        )
        self.coordinator_assistant = Person.objects.get_or_create(
            name='CoordinatorAssistant Test',
            user='CoordinatorAssistantTest',
        )
        self.adviser = Person.objects.get_or_create(
            name='Adviser Test',
            user='AdviserTest',
        )
        self.teacher = Person.objects.get_or_create(
            name='Teacher Test',
            user='TeacherTest',
        )
        self.teaching_assistant = Person.objects.get_or_create(
            name='TeachingAssistant Test',
            user='TeachingAssistantTest',
        )
        self.student = Person.objects.get_or_create(
            name='Student Test',
            user='StudentTest',
        )
        # Setup module objects
        module_assigned = Module.objects.get_or_create(
            code=1738494738393,
            name='PermissionTestModule',
        )
