import pyexcel
import pyexcel_xlsx
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# Create your tests here.
from pyexcel import Sheet

from Grades.models import *
from importer.forms import GradeUploadForm
from importer.views import make_grade, COLUMN_TITLE_ROW
from django.contrib.auth.models import User

import django_excel as excel


class GradeImportStressTest(TestCase):
    def setUp(self):

        tcs = Study.objects.create(abbreviation='TCS', name='Technical Computer Science')

        module_tcs = Module.objects.create(code='201300070', name='Parels der Informatica', start=datetime.date(2017, 1, 1), end=datetime.date(9999, 1, 1))

        user = User.objects.create(username='mverkleij', password='welkom123')

        teacher = Person.objects.create(name='Pietje Puk', university_number='m13377331', user=user)



        module_ed = ModuleEdition.objects.create(module=module_tcs, year=2017, block='A1')

        module_ed.save()

        module_parts = [
            ModulePart.objects.create(module_edition=module_ed, name='Parel {}'.format(i), teacher=[teacher]) for i in
            range(10)]

        Coordinator.objects.create(module=module_ed, person=teacher, is_assistant=False)

        tests = [Test.objects.create(name='Theory Test {}'.format(course.name), module_part=course, type='E') for course in module_parts]

        students = [Person.objects.create(name='Pietje Puk {}'.format(i), university_number='s1337{}'.format(i)) for i in range(600)]

        [Studying.objects.create(module_edition=module_ed, study=tcs, person=student, role='s') for student in students]

    def test_module_import(self):
        module = ModuleEdition.objects.get(pk=1)
        students = Person.objects.filter(studying__module_edition=module)

        tests = Test.objects.filter(module_part__module_edition=module)

        table = [['' for _ in range(len(tests) + 1)] for _ in range(COLUMN_TITLE_ROW)] + [['student_id'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.person_id] + [divmod(i, 9)[1]+1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')

        print('Testing upload')

        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        print(form.is_bound)
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/1', {'title': 'test.xlsx', 'file': file})
        self.assertRedirects(response, '/grades/modules/1/')