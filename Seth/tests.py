from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.db import models

from Grades.models import Module, Person, Study, ModuleEdition, ModulePart, Studying, Test, Grade, Teacher, Coordinator
from Seth.settings import LOGIN_URL
import permission_utils as pu


class PermissionUtilsTests(TestCase):
    study_assigned = None
    study_unassigned = None

    module = None
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
        CoordinatorTest = User.objects.get_or_create(
            username=u'CoordinatorTest',
            password=u'blablabla'
        )[0]
        CoordinatorAssistantTest = User.objects.get_or_create(
            username=u'CoordinatorAssistantTest',
            password=u'blablabla'
        )[0]
        AdviserTest = User.objects.get_or_create(
            username=u'AdviserTest',
            password=u'blablabla'
        )[0]
        TeacherTest = User.objects.get_or_create(
            username=u'TeacherTest',
            password=u'blablabla'
        )[0]
        TeachingAssistantTest = User.objects.get_or_create(
            username=u'TeachingAssistantTest',
            password=u'blablabla'
        )[0]
        StudentTest = User.objects.get_or_create(
            username=u'StudentTest',
            password=u'blablabla'
        )[0]

        # Setup Person objects
        self.coordinator = Person.objects.get_or_create(
            name='Coordinator Test',
            defaults={
                'user': CoordinatorTest,
                'university_number': 'm1'
            }
        )[0]
        self.coordinator_assistant = Person.objects.get_or_create(
            name='CoordinatorAssistant Test',
            defaults={
                'user': CoordinatorAssistantTest,
                'university_number': 'm2'
            }
        )[0]
        self.adviser = Person.objects.get_or_create(
            name='Adviser Test',
            defaults={
                'user': AdviserTest,
                'university_number': 'm3'
            }
        )[0]
        self.teacher = Person.objects.get_or_create(
            name='Teacher Test',
            defaults={
                'user': TeacherTest,
                'university_number': 'm4'
            }

        )[0]
        self.teaching_assistant = Person.objects.get_or_create(
            name='TeachingAssistant Test',
            defaults={
                'user': TeachingAssistantTest,
                'university_number': 's1'
            }

        )[0]
        self.student = Person.objects.get_or_create(
            name='Student Test',
            defaults={
                'user': StudentTest,
                'university_number': 's2'
            }

        )[0]

        # Setup study and module and modulepart objects
        self.study_assigned = Study.objects.get_or_create(
            abbreviation='PTA',
            name='Permission Test Assigned'
        )[0]
        self.study_unassigned = Study.objects.get_or_create(
            abbreviation='PTU',
            name='Permission Test Unassigned'
        )[0]
        self.module = Module.objects.get_or_create(
            name='PermissionTestModuleAss',
        )[0]
        self.module_unassigned = Module.objects.get_or_create(
            name='PermissionTestModuleUnass',
        )[0]
        self.module_ed_assigned = ModuleEdition.objects.get_or_create(
            module_code='1738494738393',
            year=2000,
            module=self.module,
            block='JAAR',
        )[0]
        self.module_ed_unassigned = ModuleEdition.objects.get_or_create(
            module_code='1738494738394',
            year=2000,
            module=self.module_unassigned,
            block='JAAR',
        )[0]
        self.module_part_assigned = ModulePart.objects.get_or_create(
            name='PermissionTest Assigned',
            module_edition=self.module_ed_assigned
        )[0]
        self.module_part_unassigned = ModulePart.objects.get_or_create(
            name='PermissionTest Unassigned',
            module_edition=self.module_ed_unassigned
        )[0]

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
        self.study_assigned.advisers.add(self.adviser)
        Teacher.objects.get_or_create(
            person=self.teacher,
            module_part = self.module_part_assigned,
            defaults={
                'role': 'T'
            }
        )
        Teacher.objects.get_or_create(
            person=self.teaching_assistant,
            module_part=self.module_part_assigned,
            defaults={
                'role': 'A'
            }
        )

        Studying.objects.get_or_create(
            person=self.student,
            module_edition=self.module_ed_assigned,
            role='Bachelor'
        )

    def test_coordinator(self):
        is_coordinator = pu.is_coordinator(self.coordinator)
        self.assertEqual(is_coordinator, True)

        is_coordinator_of_module_success = pu.is_coordinator_of_module(self.coordinator, self.module_ed_assigned)
        self.assertEqual(is_coordinator_of_module_success, True)

        is_coordinator_of_module_failure = pu.is_coordinator_of_module(self.coordinator, self.module_ed_unassigned)
        self.assertEqual(is_coordinator_of_module_failure, False)

        self.assertEqual(pu.is_coordinator_assistant(self.coordinator), False)
        self.assertEqual(pu.is_study_adviser(self.coordinator), False)
        self.assertEqual(pu.is_teacher(self.coordinator), False)
        self.assertEqual(pu.is_teaching_assistant(self.coordinator), False)
        self.assertEqual(pu.is_student(self.coordinator), False)

    def test_coordinator_assistant(self):
        is_coordinator_assistant = pu.is_coordinator_assistant(self.coordinator_assistant)
        self.assertEqual(is_coordinator_assistant, True)

        is_coordinator_assistant_of_module_success = pu.is_coordinator_assistant_of_module(self.coordinator_assistant,
                                                                                           self.module_ed_assigned)
        self.assertEqual(is_coordinator_assistant_of_module_success, True)

        is_coordinator_assistant_of_module_failure = pu.is_coordinator_assistant_of_module(self.coordinator_assistant,
                                                                                           self.module_ed_unassigned)
        self.assertEqual(is_coordinator_assistant_of_module_failure, False)

        self.assertEqual(pu.is_coordinator(self.coordinator_assistant), False)
        self.assertEqual(pu.is_study_adviser(self.coordinator_assistant), False)
        self.assertEqual(pu.is_teacher(self.coordinator_assistant), False)
        self.assertEqual(pu.is_teaching_assistant(self.coordinator_assistant), False)
        self.assertEqual(pu.is_student(self.coordinator_assistant), False)

    def test_adviser(self):
        is_adviser = pu.is_study_adviser(self.adviser)
        self.assertEqual(is_adviser, True)

        is_adviser_of_study_success = pu.is_study_adviser_of_study(self.adviser, self.study_assigned)
        # print(Study.objects.filter(pk=self.study_assigned.pk)[0].advisers.all())
        # print(self.adviser)
        self.assertEqual(is_adviser_of_study_success, True)

        is_adviser_of_study_failure = pu.is_study_adviser_of_study(self.adviser, self.study_unassigned)
        self.assertEqual(is_adviser_of_study_failure, False)

        self.assertEqual(pu.is_coordinator(self.adviser), False)
        self.assertEqual(pu.is_coordinator_assistant(self.adviser), False)
        self.assertEqual(pu.is_teacher(self.adviser), False)
        self.assertEqual(pu.is_teaching_assistant(self.adviser), False)
        self.assertEqual(pu.is_student(self.adviser), False)

    def test_teacher(self):
        is_teacher = pu.is_teacher(self.teacher)
        self.assertEqual(is_teacher, True)

        is_teacher_of_module_part_success = pu.is_teacher_of_part(self.teacher, self.module_part_assigned)
        self.assertEqual(is_teacher_of_module_part_success, True)

        is_teacher_of_module_part_failure = pu.is_teacher_of_part(self.teacher, self.module_part_unassigned)
        self.assertEqual(is_teacher_of_module_part_failure, False)

        self.assertEqual(pu.is_coordinator(self.teacher), False)
        self.assertEqual(pu.is_coordinator_assistant(self.teacher), False)
        self.assertEqual(pu.is_study_adviser(self.teacher), False)
        self.assertEqual(pu.is_teaching_assistant(self.teacher), False)
        self.assertEqual(pu.is_student(self.teacher), False)

    def test_teaching_assistant(self):
        is_teaching_assistant = pu.is_teaching_assistant(self.teaching_assistant)
        self.assertEqual(is_teaching_assistant, True)

        is_teaching_part_success = pu.is_teaching_assistant_of_part(self.teaching_assistant, self.module_part_assigned)
        self.assertEqual(is_teaching_part_success, True)

        is_teaching_part_failure = pu.is_teaching_assistant_of_part(self.teaching_assistant,
                                                                    self.module_part_unassigned)
        self.assertEqual(is_teaching_part_failure, False)

        self.assertEqual(pu.is_coordinator(self.teaching_assistant), False)
        self.assertEqual(pu.is_coordinator_assistant(self.teaching_assistant), False)
        self.assertEqual(pu.is_study_adviser(self.teaching_assistant), False)
        self.assertEqual(pu.is_teacher(self.teaching_assistant), False)
        self.assertEqual(pu.is_student(self.teaching_assistant), False)

    def test_student(self):
        is_student = pu.is_student(self.student)
        self.assertEqual(is_student, True)

        is_student_of_module_success = pu.is_student_of_module(self.student, self.module_ed_assigned)
        # print('student: ' + str(self.student.university_number))
        # print('module: ' + self.module_unassigned.code)
        # print('is_student: ' + str(is_student_of_module_success))
        self.assertEqual(is_student_of_module_success, True)

        is_student_of_module_failure = pu.is_student_of_module(self.student, self.module_ed_unassigned)
        # print('student: '+self.student.university_number)
        # print('module: '+self.module_unassigned.code)
        # print('is_student: '+str(is_student_of_module_failure))
        # print("assigned: " + self.module_ed_assigned.code)
        # print("unassigned: "+self.module_ed_unassigned.code)
        self.assertEqual(is_student_of_module_failure, False)

        self.assertEqual(pu.is_coordinator(self.student), False)
        self.assertEqual(pu.is_coordinator_assistant(self.student), False)
        self.assertEqual(pu.is_study_adviser(self.student), False)
        self.assertEqual(pu.is_teacher(self.student), False)
        self.assertEqual(pu.is_teaching_assistant(self.student), False)
