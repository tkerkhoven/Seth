import unittest

import pyexcel
import pyexcel_xlsx
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# Create your tests here.
from pyexcel import Sheet

from Grades.exceptions import GradeException
from Grades.models import *
from importer.forms import GradeUploadForm
from importer.views import make_grade, COLUMN_TITLE_ROW
from django.contrib.auth.models import User

import django_excel as excel
from django.urls import reverse

@unittest.skip("skip because of time constraints. Comment out for test.")
class ImporterStressTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(code='201300070', name='Parels der Informatica',
                                           start=datetime.date(2017, 1, 1), end=datetime.date(9999, 1, 1))

        user = User.objects.create(username='mverkleij', password='welkom123')

        teacher = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)

        module_ed = ModuleEdition.objects.create(module=module_tcs, year=2017, block='A1')

        module_ed.save()

        module_parts = [
            ModulePart.objects.create(module_edition=module_ed, name='Parel {}'.format(i), teacher=[teacher]) for i in
            range(100)]

        Coordinator.objects.create(module_edition=module_ed, person=teacher, is_assistant=False)

        tests = [Test.objects.create(name='Theory Test {}'.format(course.name), module_part=course, type='E') for course
                 in module_parts]

        students = [Person.objects.create(name='Pietje Puk {}'.format(i), university_number='s1337{}'.format(i)) for i
                    in range(600)]

        [Studying.objects.create(module_edition=module_ed, study=tcs, person=student, role='s') for student in students]

    def test_module_import(self):
        module = ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition=module)

        tests = Test.objects.filter(module_part__module_edition=module)

        table = [['' for _ in range(len(tests) + 1)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['student_id'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module.pk), {'title': 'test.xlsx', 'file': file})
        self.assertRedirects(response, '/grades/modules/{}/'.format(module.pk))


class ImporterTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(code='201300070', name='Parels der Informatica',
                                           start=datetime.date(2017, 1, 1), end=datetime.date(9999, 1, 1))

        user = User.objects.create(username='mverkleij', password='welkom123')

        teacher = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)

        module_ed = ModuleEdition.objects.create(module=module_tcs, year=2017, block='A1')

        module_ed.save()

        module_parts = [
            ModulePart.objects.create(module_edition=module_ed, name='Parel {}'.format(i), teacher=[teacher]) for i in
            range(2)]

        Coordinator.objects.create(module_edition=module_ed, person=teacher, is_assistant=False)

        tests = [Test.objects.create(name='Theory Test {}'.format(course.name), module_part=course, type='E') for course
                 in module_parts]

        students = [Person.objects.create(name='Pietje Puk {}'.format(i), university_number='s1337{}'.format(i)) for i
                    in range(2)]

        [Studying.objects.create(module_edition=module_ed, study=tcs, person=student, role='s') for student in students]

    def test_module_import(self):
        module = ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition=module)

        tests = Test.objects.filter(module_part__module_edition=module)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['student_id', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module.pk), {'title': 'test.xlsx', 'file': file})
        self.assertRedirects(response, '/grades/modules/{}/'.format(module.pk))


class ImporterPermissionsTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(code='201300070', name='Parels der Informatica',
                                           start=datetime.date(2017, 1, 1), end=datetime.date(9999, 1, 1))

        user = User.objects.create(username='mverkleij', password='welkom123')

        module_coordinator = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)

        module_ed = ModuleEdition.objects.create(module=module_tcs, year=2017, block='A1')

        module_ed.save()

        module_parts = [
            ModulePart.objects.create(module_edition=module_ed, name='Parel {}'.format(i), teacher=[module_coordinator])
            for i in
            range(10)]

        teacher = User.objects.create(username='teacher', password='welkom123')

        teacher_user = Person.objects.create(name='Teacher', university_number='m12345678', user=teacher)

        Teacher.objects.create(person=teacher_user, module_part=module_parts[0], role='T')

        Coordinator.objects.create(module_edition=module_ed, person=module_coordinator, is_assistant=False)

        tests = [Test.objects.create(name='Theory Test {}'.format(course.name), module_part=course, type='E') for course
                 in module_parts]

        students = [Person.objects.create(name='Pietje Puk {}'.format(i), university_number='s1337{}'.format(i)) for i
                    in range(4)]

        student_user = User.objects.create(username='student', password='welkom123')

        students.append(Person.objects.create(name='Student', university_number='s2453483', user=student_user))

        [Studying.objects.create(module_edition=module_ed, study=tcs, person=student, role='s') for student in students]

    def test_importer_views_without_privileges(self):
        dummyuser = User.objects.create(username='ppuk', password='welkom123')

        # Test behavior as basic user

        module = ModuleEdition.objects.all()[0]

        test = Test.objects.all()[0]

        self.client.force_login(dummyuser)

        response = self.client.get(reverse('importer:index'))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_module', args=[module.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_test', args=[test.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module', args=[module.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_test', args=[test.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_new_student'))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_student_to_module', args=[module.pk]))

        self.assertEqual(response.status_code, 403)

    def test_importer_views_as_module_coordinator(self):
        module = ModuleEdition.objects.all()[0]

        test = Test.objects.all()[0]

        self.client.force_login(User.objects.get(username='mverkleij'))

        response = self.client.get(reverse('importer:index'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'importer/mcindex.html')

        response = self.client.get(reverse('importer:import_module', args=[module.pk]))

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:import_test', args=[test.pk]))

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_module', args=[module.pk]))

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_test', args=[test.pk]))

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:import_new_student'))

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:import_student_to_module', args=[module.pk]))

        self.assertEqual(response.status_code, 200)

    def test_importer_views_as_teacher(self):
        module = ModuleEdition.objects.all()[0]

        user = User.objects.get(username='teacher')

        test = Test.objects.filter(module_part__teacher__person__user=user)[0]
        other_test = Test.objects.exclude(module_part__teacher__person__user=user)[0]

        self.client.force_login(user)

        response = self.client.get(reverse('importer:index'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'importer/teacherindex.html')

        response = self.client.get(reverse('importer:import_module', args=[module.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_test', args=[test.pk]))

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:import_test', args=[other_test.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module', args=[module.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_test', args=[test.pk]))

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_test', args=[other_test.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_new_student'))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_student_to_module', args=[module.pk]))

        self.assertEqual(response.status_code, 403)

    def test_importer_views_as_student(self):
        module = ModuleEdition.objects.all()[0]

        user = User.objects.get(username='student')

        test = Test.objects.filter(module_part__module_edition__studying__person__user=user)[0]

        self.client.force_login(user)

        response = self.client.get(reverse('importer:index'))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_module', args=[module.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_test', args=[test.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module', args=[module.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_test', args=[test.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_new_student'))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_student_to_module', args=[module.pk]))

        self.assertEqual(response.status_code, 403)


class MakeGradeTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(code='201300070', name='Parels der Informatica',
                                           start=datetime.date(2017, 1, 1), end=datetime.date(9999, 1, 1))

        user = User.objects.create(username='mverkleij', password='welkom123')

        module_coordinator = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)

        module_ed = ModuleEdition.objects.create(module=module_tcs, year=2017, block='A1')

        module_ed.save()

        module_parts = [
            ModulePart.objects.create(module_edition=module_ed, name='Parel {}'.format(i), teacher=[module_coordinator])
            for i in
            range(10)]

        teacher = User.objects.create(username='teacher', password='welkom123')

        teacher_user = Person.objects.create(name='Teacher', university_number='m12345678', user=teacher)

        Teacher.objects.create(person=teacher_user, module_part=module_parts[0], role='T')

        Coordinator.objects.create(module_edition=module_ed, person=module_coordinator, is_assistant=False)

        tests = [Test.objects.create(name='Theory Test {}'.format(course.name), module_part=course, type='E') for course
                 in module_parts]

        students = [Person.objects.create(name='Pietje Puk {}'.format(i), university_number='s1337{}'.format(i)) for i
                    in range(4)]

        student_user = User.objects.create(username='student', password='welkom123')

        students.append(Person.objects.create(name='Student', university_number='s2453483', user=student_user))

        [Studying.objects.create(module_edition=module_ed, study=tcs, person=student, role='s') for student in students]

    def test_make_grade(self):
        student = Person.objects.filter(name='Student')[0]
        corrector = Person.objects.filter(name='Teacher')[0]
        test = Test.objects.all()[0]
        grade = 1.0
        description = 'foo'

        grade_obj = make_grade(student, corrector, test, grade, description)
        grade_obj.save()

        saved_grade = Grade.objects.all()[0]

        self.assertEqual(saved_grade.student, student)
        self.assertEqual(saved_grade.teacher, corrector)
        self.assertEqual(saved_grade.test, test)
        self.assertEqual(saved_grade.grade, grade)
        self.assertEqual(saved_grade.description, description)

    def test_make_too_small_grade(self):
        student = Person.objects.filter(name='Student')[0]
        corrector = Person.objects.filter(name='Teacher')[0]
        test = Test.objects.all()[0]
        grade = float(test.minimum_grade) - 0.1
        description = 'foo'
        try:
            grade = make_grade(student, corrector, test, grade, description)
            self.fail('Grade created successfully that is too small')
        except GradeException:
            pass

    def test_make_too_large_grade(self):
        student = Person.objects.filter(name='Student')[0]
        corrector = Person.objects.filter(name='Teacher')[0]
        test = Test.objects.all()[0]
        grade = float(test.maximum_grade) + 0.1
        description = 'foo'
        try:
            grade = make_grade(student, corrector, test, grade, description)
            self.fail('Grade created successfully that is too large')
        except GradeException:
            pass

    def test_make_invalid_grade(self):
        student = Person.objects.filter(name='Student')[0]
        corrector = Person.objects.filter(name='Teacher')[0]
        test = Test.objects.all()[0]
        grade = 'e'
        description = 'foo'
        try:
            grade = make_grade(student, corrector, test, grade, description)
            self.fail('Grade created successfully that is no number')
        except GradeException:
            pass
