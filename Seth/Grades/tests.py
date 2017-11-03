import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from Grades.models import Person, Coordinator, Teacher, Grade, Test, Studying, ModulePart, ModuleEdition, Module, Study
from Grades.views import ModuleView, GradeView, StudentView, ModuleStudentView
from Seth.settings import LOGIN_URL
from module_management.tests import get_list_from_queryset


def set_up_base_data():
    # Define Users
    student_user0 = User(username='student0', password='secure_password')
    student_user1 = User(username='student1', password='secure_password')
    student_user2 = User(username='student2', password='secure_password')
    teaching_assistant_user = User(username='teaching_assistant0', password='secure_password')
    teacher_user = User(username='teacher0', password='secure_password')
    study_adviser_user = User(username='study_adviser0', password='secure_password')
    coordinator_user = User(username='coordinator0', password='secure_password')
    student_user0.save()
    student_user1.save()
    student_user2.save()
    teaching_assistant_user.save()
    teacher_user.save()
    study_adviser_user.save()
    coordinator_user.save()

    # Define Persons
    student_person0 = Person(university_number='s0', name='Student 0', user=student_user0)
    student_person2 = Person(university_number='s2', name='Student 0', user=student_user2)
    teaching_assistant_person = Person(university_number='s1', name='Teaching Assistant 0',
                                       user=teaching_assistant_user)
    teacher_person = Person(university_number='m2', name='Teacher 0', user=teacher_user)
    study_adviser_person = Person(university_number='m3', name='Study Adviser 0', user=study_adviser_user)
    coordinator_person = Person(university_number='m4', name='Coordinator 0', user=coordinator_user)
    student_person1 = Person(university_number='s5', name='Student 1', user=student_user1)
    student_person0.save()
    teaching_assistant_person.save()
    teacher_person.save()
    study_adviser_person.save()
    coordinator_person.save()
    student_person1.save()
    student_person2.save()

    # Define Modules
    module0 = Module(code='001', name='Module 1')
    module0.save()

    module1 = Module(code='002', name='Module 2')
    module1.save()

    # Define Study
    study = Study(abbreviation='STU', name='Study')
    study.save()
    study.advisers.add(study_adviser_person)
    study.modules.add(module0)

    # Define Module Editions
    module_ed0 = ModuleEdition(module=module0, block='1A', year=timezone.now().year)
    module_ed0.save()

    module_ed1 = ModuleEdition(module=module0, block='1A', year=timezone.now().year - 2)
    module_ed1.save()

    module_ed2 = ModuleEdition(module=module1, block='1B', year=timezone.now().year)
    module_ed2.save()

    module_ed3 = ModuleEdition(module=module0, block='1A', year=timezone.now().year - 1)
    module_ed3.save()

    # Define Module Parts
    module_part0 = ModulePart(name='module_part0', module_edition=module_ed0)
    module_part0.save()

    module_part1 = ModulePart(name='module_part1', module_edition=module_ed2)
    module_part1.save()

    module_part2 = ModulePart(name='module_part2', module_edition=module_ed0)
    module_part2.save()

    # Define Studying
    studying00 = Studying(person=student_person0, module_edition=module_ed0, role='student')
    studying01 = Studying(person=student_person0, module_edition=module_ed2, role='student')
    studying1 = Studying(person=student_person1, module_edition=module_ed0, role='student')
    studying2 = Studying(person=student_person2, module_edition=module_ed0, role='student')
    studying00.save()
    studying01.save()
    studying1.save()
    studying2.save()

    # Define Tests
    test0 = Test(module_part=module_part0, name='test0', type='E')
    test0.save()

    test1 = Test(module_part=module_part1, name='test1', type='E')
    test1.save()

    test2 = Test(module_part=module_part2, name='test2', type='E')
    test2.save()

    # Define Grades
    grade00 = Grade(test=test0, teacher=teacher_person, student=student_person0, description='grade0', grade=6)
    grade01 = Grade(test=test1, teacher=teacher_person, student=student_person0, description='grade1', grade=4)
    grade1 = Grade(test=test0, teacher=teacher_person, student=student_person1, description='grade0', grade=9)
    grade2 = Grade(test=test0, teacher=teacher_person, student=student_person2, description='grade0', grade=3)
    grade00.save()
    grade01.save()
    grade1.save()
    grade2.save()

    # Define Teachers
    teacher0 = Teacher(module_part=module_part0, person=teacher_person, role='T')
    teaching_assistant0 = Teacher(module_part=module_part0, person=teaching_assistant_person, role='A')
    teacher0.save()
    teaching_assistant0.save()

    # Define Coordinators
    coordinator0 = Coordinator(person=coordinator_person, module_edition=module_ed0, is_assistant=False)
    coordinator0.save()

    coordinator1 = Coordinator(person=coordinator_person, module_edition=module_ed3, is_assistant=False)
    coordinator1.save()

class GradesModuleViewTest(TestCase):
    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        self.client.logout()
        url = reverse('grades:modules')
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_sufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(reverse('grades:modules'))
        self.assertEqual(response.status_code, 302)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(reverse('grades:modules'))
        self.assertEqual(response.status_code, 200)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(reverse('grades:modules'))
        self.assertEqual(response.status_code, 200)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(reverse('grades:modules'))
        self.assertEqual(response.status_code, 200)

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(reverse('grades:modules'))
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        user = User.objects.get(username='coordinator0')

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(reverse('grades:modules'))

        self.assertEqual(response.resolver_match.func.__name__, ModuleView.as_view().__name__)
        self.assertTemplateUsed(response, 'Grades/modules.html')

        self.assertQuerysetEqual(response.context['module_list'], get_list_from_queryset(ModuleEdition.objects.filter(coordinators__user=user).order_by('-year')))

    def test_queries(self):
        user = User.objects.get(username='coordinator0')
        url_1 = reverse('grades:modules')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(12):
            self.client.get(url_1, follow=True)


class GradesGradeViewTest(TestCase):

    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        pk = ModuleEdition.objects.get(module__code='001', year=timezone.now().year).pk

        self.client.logout()
        url = reverse('grades:gradebook', kwargs={'pk': pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        pk = ModuleEdition.objects.get(module__code='001', year=timezone.now().year).pk
        url = reverse('grades:gradebook', kwargs={'pk': pk})

        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        pk = ModuleEdition.objects.get(module__code='001', year=timezone.now().year).pk
        url = reverse('grades:gradebook', kwargs={'pk': pk})

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        pk = ModuleEdition.objects.get(module__code='001', year=timezone.now().year).pk
        url = reverse('grades:gradebook', kwargs={'pk': pk})
        user = User.objects.get(username='coordinator0')

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(url)

        self.assertEqual(response.resolver_match.func.__name__, GradeView.as_view().__name__)
        self.assertTemplateUsed(response, 'Grades/gradebook.html')

    def test_queries(self):
        pk = ModuleEdition.objects.get(module__code='001', year=timezone.now().year).pk
        url = reverse('grades:gradebook', kwargs={'pk': pk})
        user = User.objects.get(username='coordinator0')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(15):
            self.client.get(url, follow=True)

class GradesStudentViewTest(TestCase):

    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        pk = Person.objects.get(university_number='s0').pk

        self.client.logout()
        url = reverse('grades:student', kwargs={'pk': pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        pk = Person.objects.get(university_number='s0').pk
        url = reverse('grades:student', kwargs={'pk': pk})

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        pk = Person.objects.get(university_number='s0').pk
        url = reverse('grades:student', kwargs={'pk': pk})

        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        pk = Person.objects.get(university_number='s0').pk
        url = reverse('grades:student', kwargs={'pk': pk})
        user = User.objects.get(username='student0')

        # Log in as student
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(url)

        self.assertEqual(response.resolver_match.func.__name__, StudentView.as_view().__name__)
        self.assertTemplateUsed(response, 'Grades/student.html')

    def test_queries(self):
        pk = Person.objects.get(university_number='s0').pk
        url = reverse('grades:student', kwargs={'pk': pk})
        user = User.objects.get(username='student0')

        # Login as student
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(16):
            self.client.get(url, follow=True)

class GradesModuleStudentViewTest(TestCase):

    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        pk = ModuleEdition.objects.get(module__code='001', year=timezone.now().year).pk
        uid = Person.objects.get(university_number='s0').pk

        self.client.logout()
        url = reverse('grades:modstudent', kwargs={'pk': pk, 'sid': uid})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        pk = ModuleEdition.objects.get(module__code='001', year=timezone.now().year).pk
        uid = Person.objects.get(university_number='s0').pk
        url = reverse('grades:modstudent', kwargs={'pk': pk, 'sid': uid})

        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        pk = ModuleEdition.objects.get(module__code='001', year=timezone.now().year).pk
        uid = Person.objects.get(university_number='s0').pk
        url = reverse('grades:modstudent', kwargs={'pk': pk, 'sid': uid})

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        pk = ModuleEdition.objects.get(module__code='001', year=timezone.now().year).pk
        uid = Person.objects.get(university_number='s0').pk
        url = reverse('grades:modstudent', kwargs={'pk': pk, 'sid': uid})
        user = User.objects.get(username='coordinator0')

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(url)

        self.assertEqual(response.resolver_match.func.__name__, ModuleStudentView.as_view().__name__)
        self.assertTemplateUsed(response, 'Grades/modulestudent.html')

    def test_queries(self):
        pk = ModuleEdition.objects.get(module__code='001', year=timezone.now().year).pk
        uid = Person.objects.get(university_number='s0').pk
        url = reverse('grades:modstudent', kwargs={'pk': pk, 'sid': uid})
        user = User.objects.get(username='coordinator0')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(17):
            self.client.get(url, follow=True)

# get/1/E?view=mod_ed&_=1509622129251
class GetDataTest(TestCase):

    def setUp(self):
        set_up_base_data()

    def test_assignments_mod_ed(self):
        pk = ModuleEdition.objects.get(module__code='001', year=timezone.now().year).pk
        url = reverse("grades:get", kwargs={'pk':pk, 't':'A'}) + "?view=mod_ed"
        user = User.objects.get(username='coordinator0')

        #Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        print(url)
        print(json_data)