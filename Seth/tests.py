from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.db import models

from Grades.models import Module, Person, Study, ModuleEdition, ModulePart, Studying, Test, Grade, Teacher, Coordinator
from Seth.settings import LOGIN_URL
from module_management.views import IndexView, ModuleView, ModuleEdView


class ModuleManagementIndexTests(TestCase):
    study_assigned = None
    study_unassigned = None

    module_assigned = None
    module_unassigned = None
    module_ed_assigned = None
    module_ed_unassigned = None

    module_part_assigned = None
    module_part_unassigned = None

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

        # Setup study and module and modulepart objects
        self.study_assigned = Study.objects.get_or_create(
            abbreviation='PTA',
            name='Permission Test Assigned'
        )
        self.study_unassigned = Study.objects.get_or_create(
            abbreviation='PTU',
            name='Permission Test Unassigned'
        )
        self.module_assigned = Module.objects.get_or_create(
            code=1738494738393,
            name='PermissionTestModuleAss',
        )
        self.module_unassigned = Module.objects.get_or_create(
            code=1738494738394,
            name='PermissionTestModuleUnass',
        )
        self.module_ed_assigned = ModuleEdition.objects.get_or_create(
            year=2000,
            module=self.module_assigned,
            block='block JAAR',
        )
        self.module_ed_unassigned = ModuleEdition.objects.get_or_create(
            year=2000,
            module=self.module_assigned,
            block='block JAAR',
        )
        self.module_part_assigned = ModulePart.objects.get_or_create(
            name='PermissionTest Assigned',
            module_edition=self.module_ed_assigned
        )
        self.module_part_unassigned = ModulePart.objects.get_or_create(
            name='PermissionTest Unassigned',
            module_edition=self.module_ed_unassigned
        )

        # Assigning persons to modules
        Coordinator.objects.get_or_create(
            person=self.coordinator,
            module_edition=self.module_ed_assigned,
            is_assistant=False,
        )
        Coordinator.objects.get_or_create(
            person=self.coordinator_assistant,
            module_edition=self.module_ed_assigned,
            is_assistant=True,
        )
        self.study_assigned.update(
            advisers=self.adviser
        )
        self.module_part_assigned.update(
            teachers=self.teacher,
            role='T'
        )
        self.module_part_assigned.update(
            teachers=self.teacher,
            role='A'
        )
        Studying.objects.get_or_create(
            person=self.student,
            study=self.study_assigned,
            module_edition=self.module_assigned,
            role='Bachelor'
        )
