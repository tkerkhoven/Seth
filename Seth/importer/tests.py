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
from importer.forms import GradeUploadForm, TestGradeUploadForm, ImportStudentModule, COLUMN_TITLE_ROW
from importer.views import make_grade
from django.contrib.auth.models import User

import django_excel as excel
from django.urls import reverse


@unittest.skip("ImporterStressTest is ignored by default. Comment out line 21 in Importer/tests.py to test.")
class ImporterStressTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(code='201300070', name='Parels der Informatica')

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

        [Studying.objects.create(module_edition=module_ed, person=student, role='s') for student in students]

    def test_module_import(self):
        module_edition = ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['' for _ in range(len(tests) + 1)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module_edition.pk), {'title': 'test.xlsx', 'file': file})
        self.assertRedirects(response, '/grades/modules/{}/'.format(module_edition.pk))


class ImporterTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(code='201300070', name='Parels der Informatica')

        user = User.objects.create(username='mverkleij', password='welkom123')

        teacher = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)

        module_ed = ModuleEdition.objects.create(module=module_tcs, year=2017, block='A1')

        module_ed2 = ModuleEdition.objects.create(module=module_tcs, year=2018, block='A1')

        module_parts = [
            ModulePart.objects.create(module_edition=module_ed, name='Parel {}'.format(i), teacher=[teacher]) for i in
            range(2)]

        module_part_2 = ModulePart.objects.create(module_edition=module_ed2, name='Parel 1', teacher=[teacher])

        Test.objects.create(name='Theory Test 1', module_part=module_part_2, type='E')

        Coordinator.objects.create(module_edition=module_ed, person=teacher, is_assistant=False)

        tests = [Test.objects.create(name='Theory Test {}'.format(course.name), module_part=course, type='E') for course
                 in module_parts]

        students = [Person.objects.create(name='Pietje Puk {}'.format(i), university_number='s1337{}'.format(i)) for i
                    in range(2)]

        [Studying.objects.create(module_edition=module_ed, person=student, role='s') for student in students]


    ### CORRECT TESTS

    def test_module_import(self):
        module_edition = ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module_edition.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        self.assertRedirects(response, '/grades/modules/{}/'.format(module_edition.pk))

    def test_module_part_import(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        #print(response.content)
        self.assertRedirects(response, '/grades/module-part/{}/'.format(module_part.pk))

    def test_test_import(self):
        module_edition = ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        test = Test.objects.filter(module_part__module_edition=module_edition)[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        table = [['' for _ in range(4)] for _ in range(COLUMN_TITLE_ROW)] + \
                [['university_number', 'name', 'grade', 'description']]

        for student in students:
            table.append([student.university_number, student.name, 6, ''])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = TestGradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/test/{}'.format(test.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        self.assertRedirects(response, '/grades/tests/{}/'.format(test.pk))


    ## TEST INVALID STUDENT NUMBER

    def test_module_import_invalid_university_number(self):
        module_edition = ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number + '1', student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module_edition.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})

        self.assertTrue('Enroll these students first before retrying' in response.content.decode())
        for student in students:
            self.assertTrue(student.university_number + '1' in response.content.decode())

    def test_module_part_import_invalid_university_number(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number + '1', student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})

        self.assertTrue('Enroll these students first before retrying' in response.content.decode())
        for student in students:
            self.assertTrue(student.university_number + '1' in response.content.decode())

    def test_test_import_invalid_university_number(self):
        module_edition = ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        test = Test.objects.filter(module_part__module_edition=module_edition)[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        table = [['' for _ in range(4)] for _ in range(COLUMN_TITLE_ROW)] + \
                [['university_number', 'name', 'grade', 'description']]

        for student in students:
            table.append([student.university_number + '1', student.name, 6, ''])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = TestGradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/test/{}'.format(test.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})

        self.assertTrue('Enroll these students first before retrying' in response.content.decode())
        for student in students:
            self.assertTrue(student.university_number + '1' in response.content.decode())


    ### INVALID GRADE

    def test_module_import_invalid_grade(self):
        module_edition = \
        ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append(
                [student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        table[-1][2] = 'a'

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})

        self.assertTrue('GradeException' in response.content.decode())

    def test_module_part_import_invalid_grade(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append(
                [student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        table[-1][2] = 'a'

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        self.assertTrue('GradeException' in response.content.decode())

    def test_test_import_invalid_grade(self):
        module_edition = \
        ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        test = Test.objects.filter(module_part__module_edition=module_edition)[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        table = [['' for _ in range(4)] for _ in range(COLUMN_TITLE_ROW)] + \
                [['university_number', 'name', 'grade', 'description']]

        for student in students:
            table.append([student.university_number, student.name, 6, ''])

        table[-1][2] = 'a'

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = TestGradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/test/{}'.format(test.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        self.assertTrue('GradeException' in response.content.decode())



    ### INVALID TEST

    def test_module_import_invalid_test(self):
        module_edition = \
        ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.all()

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append(
                [student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        print(response.content)
        self.assertTrue('Attempt to register grades for a test that is not part of this module.' in response.content.decode())

    def test_module_part_import_invalid_test(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.all()

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append(
                [student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])
        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        self.assertTrue('Attempt to register grades for a test that is not part of this module.' in response.content.decode())

    def test_test_import_invalid_test(self):
        module_edition = \
        ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        test = Test.objects.exclude(module_part__module_edition=module_edition)[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        table = [['' for _ in range(4)] for _ in range(COLUMN_TITLE_ROW)] + \
                [['university_number', 'name', 'grade', 'description']]

        for student in students:
            table.append([student.university_number, student.name, 6, ''])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = TestGradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/test/{}'.format(test.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        self.assertEqual(response.status_code, 403)



    ### Extra columns

    def test_module_import_extra_columns(self):
        module_edition = \
        ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['' for _ in range(len(tests) + 3)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests] + ['a']]

        for student in students:
            table.append(
                [student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))] + [''])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        self.assertRedirects(response, '/grades/modules/{}/'.format(module_edition.pk))

    def test_module_part_import_extra_columns(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

        table = [['' for _ in range(len(tests) + 3)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests] + ['a']]

        for student in students:
            table.append(
                [student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))] + [''])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        # print(response.content)
        self.assertRedirects(response, '/grades/module-part/{}/'.format(module_part.pk))

    def test_test_import_extra_columns(self):
        module_edition = \
        ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        test = Test.objects.filter(module_part__module_edition=module_edition)[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        table = [['' for _ in range(5)] for _ in range(COLUMN_TITLE_ROW)] + \
                [['university_number', 'name', 'grade', 'description'] + ['a']]

        for student in students:
            table.append([student.university_number, student.name, 6, ''] + [''])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = TestGradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/test/{}'.format(test.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        self.assertRedirects(response, '/grades/tests/{}/'.format(test.pk))


    ### EXTRA ROWS

    def test_module_import_extra_row(self):
        module_edition = ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        table.append(['' for _ in range(len(tests) + 1)] + [3])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module_edition.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        self.assertRedirects(response, '/grades/modules/{}/'.format(module_edition.pk))

    def test_module_part_import_extra_row(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        table.append(['' for _ in range(len(tests) + 1)] + [3])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        #print(response.content)
        self.assertRedirects(response, '/grades/module-part/{}/'.format(module_part.pk))

    def test_test_import_extra_row(self):
        module_edition = ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        test = Test.objects.filter(module_part__module_edition=module_edition)[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        table = [['' for _ in range(4)] for _ in range(COLUMN_TITLE_ROW)] + \
                [['university_number', 'name', 'grade', 'description']]

        for student in students:
            table.append([student.university_number, student.name, 6, ''])

        table.append(['' for _ in range(3)] + ['a'])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = TestGradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/test/{}'.format(test.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW})
        self.assertTrue('There are grades or description fields in this excel sheet that do not have a student number '
                        'filled in. Please check the contents of your excel file for stale values in rows.'
                        in response.content.decode())


    ## STUDENT IMPORT

    def test_student_import(self):
        module_edition = ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        table = [['university_number', 'name', 'email', 'role']]

        university_number = 's54321'

        table.append([university_number, 'Pietje PPPuk', 'leet@example.com', 's'])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = ImportStudentModule(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/import-module-student/{}'.format(module_edition.pk), {'title': 'test.xlsx', 'file': file})
        self.assertTemplateUsed(response, 'importer/students-module-imported.html')

        if not Person.objects.filter(university_number=university_number):
            self.fail('Person imported to module does not exist.')
        if not Studying.objects.filter(person__university_number=university_number).filter(module_edition=module_edition):
            self.fail('Studying imported to module does not exist.')


class ImporterPermissionsTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(code='201300070', name='Parels der Informatica')

        user = User.objects.create(username='mverkleij', password='welkom123')

        module_coordinator = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)

        module_ed = ModuleEdition.objects.create(module=module_tcs, year=2017, block='A1')
        module_ed_2 = ModuleEdition.objects.create(module=module_tcs, year=2018, block='A1')

        module_parts = [
            ModulePart.objects.create(module_edition=module_ed, name='Parel {}'.format(i), teacher=[module_coordinator])
            for i in
            range(10)]

        teacher = User.objects.create(username='teacher', password='welkom123')

        teacher_user = Person.objects.create(name='Teacher', university_number='m12345678', user=teacher)

        Teacher.objects.create(person=teacher_user, module_part=module_parts[0], role='T')
        Teacher.objects.create(person=teacher_user, module_part=module_parts[1], role='A')

        Coordinator.objects.create(module_edition=module_ed, person=module_coordinator, is_assistant=False)
        Coordinator.objects.create(module_edition=module_ed_2, person=module_coordinator, is_assistant=True)

        tests = [Test.objects.create(name='Theory Test {}'.format(course.name), module_part=course, type='E') for course
                 in module_parts]

        students = [Person.objects.create(name='Pietje Puk {}'.format(i), university_number='s1337{}'.format(i)) for i
                    in range(4)]

        student_user = User.objects.create(username='student', password='welkom123')

        students.append(Person.objects.create(name='Student', university_number='s2453483', user=student_user))

        [Studying.objects.create(module_edition=module_ed, person=student, role='s') for student in students]

    def test_importer_views_without_privileges(self):
        dummyuser = User.objects.create(username='ppuk', password='welkom123')

        # Test behavior as basic user

        module_edition = ModuleEdition.objects.filter(year='2017')[0]

        test = module_edition.modulepart_set.all()[0].test_set.all()[0]

        self.client.force_login(dummyuser)

        response = self.client.get(reverse('importer:index'))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_module_part', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_test', args=[test.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module_part', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module_part_signoff', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_test', args=[test.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_student_to_module', args=[module_edition.pk]))

        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_student_to_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_module_structure', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module_structure', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

    def test_importer_views_as_module_coordinator(self):
        module_edition = ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        test = Test.objects.filter(module_part__module_edition=module_edition)[0]

        self.client.force_login(User.objects.get(username='mverkleij'))

        response = self.client.get(reverse('importer:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'importer/mcindex2.html')

        response = self.client.get(reverse('importer:import_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:import_module_part', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:import_test', args=[test.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_module_part', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_module_part_signoff', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_test', args=[test.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:import_student_to_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_student_to_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:import_module_structure', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_module_structure', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 200)

    def test_importer_views_as_teacher(self):
        user = User.objects.get(username='teacher')

        module_edition = ModuleEdition.objects.filter(modulepart__teacher__person__user__username='teacher')[0]

        test = Test.objects.filter(module_part__teacher__person__user=user)[0]
        other_test = Test.objects.exclude(module_part__teacher__person__user=user)[0]

        self.client.force_login(user)

        response = self.client.get(reverse('importer:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'importer/mcindex2.html')

        response = self.client.get(reverse('importer:import_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_module_part', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:import_module_part', args=[other_test.module_part.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_test', args=[test.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:import_test', args=[other_test.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module_part', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_module_part', args=[other_test.module_part.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module_part_signoff', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_module_part_signoff', args=[other_test.module_part.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_test', args=[test.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('importer:export_test', args=[other_test.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_student_to_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_student_to_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_module_structure', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module_structure', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

    def test_importer_views_as_student(self):
        module_edition = ModuleEdition.objects.all()[0]

        user = User.objects.get(username='student')

        test = Test.objects.filter(module_part__module_edition__studying__person__user=user)[0]

        self.client.force_login(user)

        response = self.client.get(reverse('importer:index'))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_module_part', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_test', args=[test.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module_part', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module_part', args=[test.module_part.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_test', args=[test.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_student_to_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_student_to_module', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:import_module_structure', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('importer:export_module_structure', args=[module_edition.pk]))
        self.assertEqual(response.status_code, 403)


class MakeGradeTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(code='201300070', name='Parels der Informatica')

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

        [Studying.objects.create(module_edition=module_ed, person=student, role='s') for student in students]

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
