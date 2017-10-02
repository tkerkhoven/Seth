import pyexcel
import pyexcel_xlsx
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# Create your tests here.
from pyexcel import Sheet

from Grades.models import *
from importer.forms import GradeUploadForm
from importer.views import make_grade
from django.contrib.auth.models import User

import django_excel as excel


class GradeImportStressTest(TestCase):
    def setUp(self):

        tcs = Study.objects.create(short_name='TCS', full_name='Technical Computer Science')

        module_tcs = Module.objects.create(module_code='201300070', name='Parels der Informatica', start=datetime.date(2017, 1, 1), stop=datetime.date(9999, 1, 1))

        user = User.objects.create(username='mverkleij', password='welkom123')

        teacher = Person.objects.create(name='Pietje Puk', id_prefix='m', person_id='13377331', user=user)

        courses = [Course.objects.create(code='201300070', code_extension='_{}'.format(i), name='Parel {}'.format(i), teacher=[teacher]) for i in range(100)]

        module_ed = Module_ed.objects.create(module=module_tcs, year=datetime.date(2017, 1, 1), module_code_extension='_2017')

        module_ed.courses = courses

        module_ed.save()

        Coordinator.objects.create(module=module_ed, person=teacher, mc_assistant=False)

        tests = [Test.objects.create(name='Theory Test', course_id=course, _type='E') for course in courses]

        students = [Person.objects.create(name='Pietje Puk {}'.format(i), id_prefix='s', person_id='1337{}'.format(i)) for i in range(600)]

        [Studying.objects.create(module_id=module_ed, study=tcs, student_id=student, role='s') for student in students]

    def test_module_import(self):
        module = Module_ed.objects.get(pk=1)
        students = Person.objects.filter(studying__module_id=module)

        tests = Test.objects.filter(course_id__module_ed=module)

        table = [['student_id'] + [test.pk for test in tests]]

        for student in students:
            table.append([student.person_id] + [divmod(i, 9)[1]+1 for i in range(len(tests))])

        sheet = Sheet(sheet=table)

        content = sheet.save_as(filename='test.xlsx')

        self.client.force_login(User.objects.get(username='mverkleij'))
        form = GradeUploadForm(files={'file': SimpleUploadedFile('test.xlsx', open('test.xlsx', 'rb').read())})
        print(form.is_bound)
        file = ContentFile(open('test.xlsx', 'rb').read())
        file.name = 'test.xlsx'

        response = self.client.post('/importer/module/1', {'title': 'test.xlsx', 'file': file})
        print(response.content)
        self.assertRedirects(response, '/grades/modules/1/')