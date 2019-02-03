import unittest
from collections import OrderedDict

from django.core.exceptions import SuspiciousOperation
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
# Create your tests here.
from pyexcel import Sheet, Book

from Grades.exceptions import GradeException
from Grades.models import *
from importer.forms import GradeUploadForm, TestGradeUploadForm, ImportStudentModule, COLUMN_TITLE_ROW, ImportModuleForm
from importer.views import make_grade


@unittest.skip("ImporterStressTest is ignored by default. Comment out line 16 in Importer/tests.py to test.")
class ImporterStressTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(name='Parels der Informatica')

        user = User.objects.create(username='mverkleij', password='welkom123')

        teacher = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)

        module_ed = ModuleEdition.objects.create(module_code='201300070', module=module_tcs, year=2017, block='A1')

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

        response = self.client.post('/importer/module/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertRedirects(response, '/grades/modules/{}/'.format(module_edition.pk))


class ImportModuleViewTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(name='Parels der Informatica')

        user = User.objects.create(username='mverkleij', password='welkom123')

        teacher = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)

        module_ed = ModuleEdition.objects.create(module_code='201300070', module=module_tcs, year=2017, block='A1')

        module_ed2 = ModuleEdition.objects.create(module_code='201300070', module=module_tcs, year=2018, block='A1')

        module_parts = [
            ModulePart.objects.create(module_edition=module_ed, name='Parel {}'.format(i), teacher=[teacher]) for i in
            range(2)]

        module_part_2 = ModulePart.objects.create(module_edition=module_ed2, name='Parel 3', teacher=[teacher])

        Test.objects.create(name='Theory Test 1', module_part=module_part_2, type='E')

        Coordinator.objects.create(module_edition=module_ed, person=teacher, is_assistant=False)

        tests = [Test.objects.create(name='Theory Test {}'.format(course.name), module_part=course, type='E') for course
                 in module_parts]

        students = [Person.objects.create(name='Pietje Puk {}'.format(i), university_number='s1337{}'.format(i)) for i
                    in range(2)]

        [Studying.objects.create(module_edition=module_ed, person=student, role='s') for student in students]

    # CORRECT TESTS

    def test_module_description_import(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.name + str for test in tests for str in ['', '_description'] ]]

        for student in students:
            table.append([student.university_number, student.name] + ['{}{}'.format((divmod(i, 9)[1] + 1), string)
                                                                      if i != 1 else ''
                                                                      for i in range(len(tests))
                                                                      for string in ['', ' Goed gedaan']])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = ImportModuleForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'
        #
        response = self.client.post('/importer/import_module/{}'.format(module_edition.pk), {'title': 'test.xlsx',
                                                                                      'file': file,
                                                                                      'title_row': COLUMN_TITLE_ROW + 1
                                                                                      })
        self.assertTemplateUsed(response, template_name='importer/successfully_imported.html')


class ImporterTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(name='Parels der Informatica')

        user = User.objects.create(username='mverkleij', password='welkom123')

        teacher = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)

        module_ed = ModuleEdition.objects.create(module_code='201300070', module=module_tcs, year=2017, block='A1')

        module_ed2 = ModuleEdition.objects.create(module_code='201300070', module=module_tcs, year=2018, block='A1')

        module_parts = [
            ModulePart.objects.create(module_edition=module_ed, name='Parel {}'.format(i), teacher=[teacher]) for i in
            range(2)]

        module_part_2 = ModulePart.objects.create(module_edition=module_ed2, name='Parel 3', teacher=[teacher])

        Test.objects.create(name='Theory Test 1', module_part=module_part_2, type='E')

        Coordinator.objects.create(module_edition=module_ed, person=teacher, is_assistant=False)

        tests = [Test.objects.create(name='Theory Test {}'.format(course.name), module_part=course, type='E') for course
                 in module_parts]

        students = [Person.objects.create(name='Pietje Puk {}'.format(i), university_number='s1337{}'.format(i)) for i
                    in range(2)]

        [Studying.objects.create(module_edition=module_ed, person=student, role='s') for student in students]

    # CORRECT TESTS

    def test_module_import(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number, student.name] + [divmod(i, 9)[1] + 1 if i != 1 else '' for i in
                                                                      range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module_edition.pk), {'title': 'test.xlsx',
                                                                                      'file': file,
                                                                                      'title_row': COLUMN_TITLE_ROW + 1
                                                                                      })

        self.assertTemplateUsed(response, template_name='importer/successfully_imported.html')

    def test_module_part_import(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number, student.name] + [divmod(i, 9)[1] + 1 if i != 1 else '' for i in
                                                                      range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTemplateUsed(response, template_name='importer/successfully_imported.html')

    def test_test_import(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

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

        response = self.client.post('/importer/test/{}'.format(test.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertRedirects(response, '/grades/tests/{}/'.format(test.pk))

    # Test import by name

    def test_module_import_by_name(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.name for test in tests]]

        for student in students:
            table.append([student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})

        self.assertTemplateUsed(response, template_name='importer/successfully_imported.html')

    def test_module_part_import_by_name(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.name for test in tests]]

        for student in students:
            table.append([student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTemplateUsed(response, template_name='importer/successfully_imported.html')

    # TEST INVALID STUDENT NUMBER

    def test_module_import_invalid_university_number(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append(
                [student.university_number + '1', student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        try:
            response = self.client.post('/importer/module/{}'.format(module_edition.pk), {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        except SuspiciousOperation as e:
            self.assertTrue('Enroll these students first before retrying' in e)
            for student in students:
                self.assertTrue(student.university_number + '1' in e)



    def test_module_part_import_invalid_university_number(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['university_number', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append(
                [student.university_number + '1', student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})

        self.assertTrue('Enroll these students first before retrying' in response.content.decode())
        for student in students:
            self.assertTrue(student.university_number + '1' in response.content.decode())

    def test_test_import_invalid_university_number(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

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

        response = self.client.post('/importer/test/{}'.format(test.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})

        self.assertTrue('Enroll these students first before retrying' in response.content.decode())
        for student in students:
            self.assertTrue(student.university_number + '1' in response.content.decode())

    # INVALID GRADE

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
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})

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
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        # print(response.content.decode())
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

        response = self.client.post('/importer/test/{}'.format(test.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTrue('GradeException' in response.content.decode())

    # INVALID TEST

    @unittest.skip("Checking this was removed and is now ignored silently instead.")
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
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTrue(
            'Attempt to register grades for a test that is not part of this module.' in response.content.decode())

    @unittest.skip("Checking this was removed and is now ignored silently instead.")
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
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTrue(
            'Attempt to register grades for a test that is not part of this module' in response.content.decode())

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

        response = self.client.post('/importer/test/{}'.format(test.pk), {'title': 'test.xlsx', 'file': file})
        self.assertEqual(response.status_code, 403)

    # Extra columns

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
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})

        self.assertTemplateUsed(response, template_name='importer/successfully_imported.html')

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
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTemplateUsed(response, template_name='importer/successfully_imported.html')

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

        response = self.client.post('/importer/test/{}'.format(test.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertRedirects(response, '/grades/tests/{}/'.format(test.pk))

    # Too little columns

    def test_test_import_too_little_columns(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        test = Test.objects.filter(module_part__module_edition=module_edition)[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        table = [['' for _ in range(5)] for _ in range(COLUMN_TITLE_ROW)] + \
                [['university_number', 'name', 'grade']]

        for student in students:
            table.append([student.university_number, student.name, 6])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = TestGradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/test/{}'.format(test.pk), {'title': 'test.xlsx', 'file': file,
                                                                          'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTrue('One of the required field [student_id, grade, description] could not be found.'
                        in response.content.decode())

        table = [['' for _ in range(5)] for _ in range(COLUMN_TITLE_ROW)] + \
                [['university_number', 'name', 'grade', '']]

        for student in students:
            table.append([student.university_number, student.name, 6, ''])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = TestGradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/test/{}'.format(test.pk), {'title': 'test.xlsx', 'file': file,
                                                                          'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTrue('One of the required field [student_id, grade, description] could not be found.'
                        in response.content.decode())

    # No tests

    def test_module_import_no_tests(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['', ''] for _ in range(COLUMN_TITLE_ROW)] + [['university_number', 'name']]

        for student in students:
            table.append(
                [student.university_number, student.name])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTrue('There were no tests recognized to import' in response.content.decode())

    def test_module_part_import_no_tests(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

        table = [['', ''] for _ in range(COLUMN_TITLE_ROW)] + [['university_number', 'name']]

        for student in students:
            table.append(
                [student.university_number, student.name])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTrue('There were no tests recognized to import' in response.content.decode())

    # No tests

    def test_module_import_no_university_number(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['wrong', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTemplateUsed(response, template_name='importer/successfully_imported.html')

    def test_module_part_import_no_university_number(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

        table = [['' for _ in range(len(tests) + 2)] for _ in range(COLUMN_TITLE_ROW)] + [
            ['wrong', 'name'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.university_number, student.name] + [divmod(i, 9)[1] + 1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTemplateUsed(response, template_name='importer/successfully_imported.html')

    # EXTRA ROWS

    def test_module_import_extra_row(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
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

        response = self.client.post('/importer/module/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})

        self.assertTemplateUsed(response, template_name='importer/successfully_imported.html')

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

        response = self.client.post('/importer/module_part/{}'.format(module_part.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTemplateUsed(response, template_name='importer/successfully_imported.html')

    def test_test_import_extra_row(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

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

        response = self.client.post('/importer/test/{}'.format(test.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTrue('There are grades or description fields in this excel sheet that do not have a student number '
                        'filled in. Please check the contents of your excel file for stale values in rows.'
                        in response.content.decode())

    # INVALID TITLE_ROWS

    def test_module_import_too_small_title_row(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

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
                                    {'title': 'test.xlsx', 'file': file, 'title_row': -1})
        self.assertTrue('The file that was uploaded was not recognised as a grade excel file. Are you '
                        'sure the file is an .xlsx file? Otherwise, download a new gradesheet and try '
                        'using that instead.'
                        in response.content.decode())

    def test_module_part_too_small_title_row(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

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
                                    {'title': 'test.xlsx', 'file': file, 'title_row': -1})
        self.assertTrue('The file uploaded was not recognised as a grade excel file. Are you '
                        'sure the file is an .xlsx file? Otherwise, download a new gradesheet and try '
                        'using that instead'
                        in response.content.decode())

    def test_module_import_too_large_title_row(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]
        students = Person.objects.filter(studying__module_edition=module_edition)

        tests = Test.objects.filter(module_part__module_edition=module_edition)

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
                                    {'title': 'test.xlsx', 'file': file, 'title_row': len(table) + 2})
        self.assertTrue('The file that was uploaded was not recognised as a grade excel file.'
                        in response.content.decode())

    def test_module_part_too_large_title_row(self):
        module_part = ModulePart.objects.filter(module_edition__coordinator__person__user__username='mverkleij')[0]
        students = Person.objects.filter(studying__module_edition__modulepart=module_part)

        tests = Test.objects.filter(module_part=module_part)

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
                                    {'title': 'test.xlsx', 'file': file, 'title_row': len(table) + 2})
        self.assertTrue('The file that was uploaded was not recognised as a grade excel file.'
                        in response.content.decode())

    # STUDENT IMPORT

    def test_student_import(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        table = [['university_number', 'name', 'email', 'role']]

        university_number = 's54321'

        table.append([university_number, 'Pietje PPPuk', 'leet@example.com', 's'])

        university_number = '54221'

        table.append([university_number, 'Pietje PPuk', 'baz@example.com', 's'])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = ImportStudentModule(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/import-module-student/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file})
        self.assertTemplateUsed(response, 'importer/students-module-imported.html')

        if not Person.objects.filter(university_number=university_number):
            self.fail('Person imported to module does not exist.')
        if not Studying.objects.filter(person__university_number=university_number).filter(
                module_edition=module_edition):
            self.fail('Studying imported to module does not exist.')

    def test_student_import_no_employees(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        table = [['university_number', 'name', 'email', 'role']]

        university_number = 'm54321'

        table.append([university_number, 'Pietje PPPuk', 'leet@example.com', 's'])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = ImportStudentModule(
            files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/import-module-student/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file})
        self.assertTrue('Trying to add an employee as a student to a module.' in response.content.decode())

    def test_student_import_not_university_number(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        table = [['university_number', 'name', 'email', 'role']]

        university_number = 'makls'

        table.append([university_number, 'Pietje PPPuk', 'leet@example.com', 's'])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = ImportStudentModule(
            files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/import-module-student/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file})
        self.assertTrue('is not a student number' in response.content.decode())

    def test_student_import_already_there(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        table = [['university_number', 'name', 'email', 'role']]

        university_number = 's13371'

        table.append([university_number, 'Pietje PPPuk', 'leet@example.com', 's'])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        form = ImportStudentModule(
            files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/import-module-student/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file})
        self.assertTemplateUsed(response, 'importer/students-module-imported.html')

        self.assertEqual(
            [['Pietje PPPuk', 's13371', 'Parels der Informatica', '2017-201300070-A1']],
            response.context[0]['context']['failed']
        )

        if not Person.objects.filter(university_number=university_number):
            self.fail('Person imported to module does not exist.')
        if not Studying.objects.filter(person__university_number=university_number).filter(
                module_edition=module_edition):
            self.fail('Studying imported to module does not exist.')

    def test_student_import_missing_columns(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        tables = [[['', 'name', 'email', 'role']],
                  [['university_number', '', 'email', 'role']],
                  [['university_number', 'name', '', 'role']],
                  [['university_number', 'name', 'email', '']]]

        for table in tables:

            university_number = 'm54321'

            table.append([university_number, 'Pietje PPPuk', 'leet@example.com', 's'])

            sheet = Sheet(sheet=table)

            sheet.save_as(filename='test.xlsx')
            self.client.force_login(User.objects.get(username='mverkleij'))
            file = ContentFile(open('test.xlsx', 'rb').read())
            file.name = 'test.xlsx'

            response = self.client.post('/importer/import-module-student/{}'.format(module_edition.pk),
                                        {'title': 'test.xlsx', 'file': file})
            self.assertTrue('Not all required columns [university_number, name, email, role] are in the excel sheet'
                            in response.content.decode())

    def test_student_import_too_little_rows(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        table = [['university_number', 'name', 'e-mail', 'role']]

        sheet = Sheet(sheet=table)

        sheet.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/import-module-student/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file})
        self.assertTrue('Not all required columns [university_number, name, email, role] are in the excel sheet, or no rows to import.'
                        in response.content.decode())

    # MODULE STRUCTURE IMPORT

    def test_module_structure_import(self):
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        new_module_part_name = 'New One'
        new_test_name = 'New test'
        new_signoff_name = 'New signoff'

        table = OrderedDict()

        table['sheet1'] = [
            ['Module part:', new_module_part_name, ''],
            ['Test name:', new_test_name, new_signoff_name],
            ['min. grade', 1, 0],
            ['max. grade', 10, 1]
        ]
        table['sheet2'] = [
            ['Module part:', new_module_part_name + ' 2', ''],
            ['Test name:', new_test_name + ' 2', new_signoff_name + ' 2'],
            ['min. grade', 1, 0],
            ['max. grade', 10, 1]
        ]

        book = Book(sheets=table)

        book.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/import-module-structure/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertRedirects(response, reverse('module_management:module_edition_detail', args=[module_edition.pk]))

        module_part_1 = ModulePart.objects.filter(module_edition=module_edition, name=new_module_part_name).first()
        if not module_part_1:
            self.fail('First page of sheet not imported correctly')
        if not Test.objects.filter(module_part=module_part_1, name=new_test_name, type='E'):
            self.fail('First test not imported correctly (at all or as exam)')
        if not Test.objects.filter(module_part=module_part_1, name=new_signoff_name, type='A'):
            self.fail('First signoff not imported correctly (at all or as exam)')

        module_part_2 = ModulePart.objects.filter(module_edition=module_edition,
                                                  name=new_module_part_name + ' 2').first()
        if not ModulePart.objects.filter(module_edition=module_edition, name=new_module_part_name + ' 2'):
            self.fail('Second page of sheet not imported correctly')
        if not Test.objects.filter(module_part=module_part_2, name=new_test_name + ' 2', type='E'):
            self.fail('Second test not imported correctly (at all or as exam)')
        if not Test.objects.filter(module_part=module_part_2, name=new_signoff_name + ' 2', type='A'):
            self.fail('Second signoff not imported correctly (at all or as exam)')

        # Test whether object removal works fine
        self.assertEqual(ModulePart.objects.filter(module_edition=module_edition).count(), 2)
        self.assertEqual(Test.objects.filter(module_part__module_edition=module_edition).count(), 4)

    # Requires test_import_module_structure to pass.
    def test_module_structure_import_failure_grades_exist(self):

        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

        # This should be the amount of module parts and testa after setup. We need this later.
        self.assertEqual(ModulePart.objects.filter(module_edition=module_edition).count(), 2)
        self.assertEqual(Test.objects.filter(module_part__module_edition=module_edition).count(), 2)

        Grade.objects.create(
            grade=8,
            test=Test.objects.filter(module_part__module_edition=module_edition).first(),
            student=Person.objects.filter(university_number__startswith="s").first(),
            teacher=Person.objects.filter(coordinator__module_edition=module_edition).first()
        )

        new_module_part_name = 'New One'
        new_test_name = 'New test'
        new_signoff_name = 'New signoff'

        table = OrderedDict()

        table['sheet1'] = [
            ['Module part:', new_module_part_name, ''],
            ['Test name:', new_test_name, new_signoff_name],
            ['min. grade', 1, 0],
            ['max. grade', 10, 1]
        ]
        table['sheet2'] = [
            ['Module part:', new_module_part_name + ' 2', ''],
            ['Test name:', new_test_name + ' 2', new_signoff_name + ' 2'],
            ['min. grade', 1, 0],
            ['max. grade', 10, 1]
        ]

        book = Book(sheets=table)

        book.save_as(filename='test.xlsx')
        self.client.force_login(User.objects.get(username='mverkleij'))
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/import-module-structure/{}'.format(module_edition.pk),
                                    {'title': 'test.xlsx', 'file': file, 'title_row': COLUMN_TITLE_ROW + 1})
        self.assertTemplateUsed(response, 'importer/module_structure_import_error.html')

        if ModulePart.objects.filter(module_edition=module_edition, name=new_module_part_name).first():
            self.fail('Made module part while atomicity should revert original state.')
        # Test whether all moduleparts are restored correctly.
        self.assertEqual(ModulePart.objects.filter(module_edition=module_edition).count(), 2)
        self.assertEqual(Test.objects.filter(module_part__module_edition=module_edition).count(), 2)
        if ModulePart.objects.filter(name=new_module_part_name):
            self.fail("Imported module part from sheet when it shoudn't")


class ImporterPermissionsTest(TestCase):
    def setUp(self):
        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(name='Parels der Informatica')

        user = User.objects.create(username='mverkleij', password='welkom123')

        module_coordinator = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)

        module_ed = ModuleEdition.objects.create(module_code='201300070', module=module_tcs, year=2017, block='A1')
        module_ed_2 = ModuleEdition.objects.create(module_code='201300070', module=module_tcs, year=2018, block='A1')

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
        module_edition = \
            ModuleEdition.objects.filter(coordinator__person__user__username='mverkleij').filter(year='2017')[0]

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
        other_test = Test.objects.filter(module_part__module_edition=module_edition).exclude(module_part__teacher__person__user=user)[0]

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

        module_tcs = Module.objects.create(name='Parels der Informatica')

        user = User.objects.create(username='mverkleij', password='welkom123')

        module_coordinator = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)

        module_ed = ModuleEdition.objects.create(module_code='201300070', module=module_tcs, year=2017, block='A1')

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

        # Create sign-off exercise
        Test.objects.create(name='signoff1', module_part=module_parts[0], minimum_grade=0.0, maximum_grade=1.0, type='A')

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

    def test_make_signoff_grade(self):
        student = Person.objects.filter(name='Student')[0]
        corrector = Person.objects.filter(name='Teacher')[0]
        test = Test.objects.filter(type='A').first()
        grade = 'MV'
        description = 'foo'

        grade_obj = make_grade(student, corrector, test, grade, description)
        grade_obj.save()

        saved_grade = Grade.objects.all()[0]

        self.assertEqual(saved_grade.student, student)
        self.assertEqual(saved_grade.teacher, corrector)
        self.assertEqual(saved_grade.test, test)
        self.assertEqual(saved_grade.grade, 1)
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
