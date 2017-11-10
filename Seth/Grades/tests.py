import json
from collections import OrderedDict

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from Grades.models import Person, Coordinator, Teacher, Grade, Test, Studying, ModulePart, ModuleEdition, Module, Study
from Grades.views import ModuleView, GradeView, StudentView, ModuleStudentView, create_grades_query, TestView, \
    ModulePartView
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
    module0 = Module(name='Module 1')
    module0.save()

    module1 = Module(name='Module 2')
    module1.save()

    # Define Study
    study = Study(abbreviation='STU', name='Study')
    study.save()
    study.advisers.add(study_adviser_person)
    study.modules.add(module0)

    # Define Module Editions
    module_ed0 = ModuleEdition(module_code='001', module=module0, block='1A', year=timezone.now().year)
    module_ed0.save()

    module_ed1 = ModuleEdition(module_code='001', module=module0, block='1A', year=timezone.now().year - 2)
    module_ed1.save()

    module_ed2 = ModuleEdition(module_code='002', module=module1, block='1B', year=timezone.now().year)
    module_ed2.save()

    module_ed3 = ModuleEdition(module_code='002', module=module0, block='1A', year=timezone.now().year - 1)
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

        self.assertQuerysetEqual(response.context['module_list'], get_list_from_queryset(
            ModuleEdition.objects.filter(coordinators__user=user).order_by('-year')))

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
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk

        self.client.logout()
        url = reverse('grades:gradebook', kwargs={'pk': pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk
        url = reverse('grades:gradebook', kwargs={'pk': pk})

        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk
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
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk
        url = reverse('grades:gradebook', kwargs={'pk': pk})
        user = User.objects.get(username='coordinator0')

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(url)

        self.assertEqual(response.resolver_match.func.__name__, GradeView.as_view().__name__)
        self.assertTemplateUsed(response, 'Grades/gradebook.html')


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
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk
        uid = Person.objects.get(university_number='s0').pk

        self.client.logout()
        url = reverse('grades:modstudent', kwargs={'pk': pk, 'sid': uid})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk
        uid = Person.objects.get(university_number='s0').pk
        url = reverse('grades:modstudent', kwargs={'pk': pk, 'sid': uid})

        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk
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
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk
        uid = Person.objects.get(university_number='s0').pk
        url = reverse('grades:modstudent', kwargs={'pk': pk, 'sid': uid})
        user = User.objects.get(username='coordinator0')

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(url)

        self.assertEqual(response.resolver_match.func.__name__, ModuleStudentView.as_view().__name__)
        self.assertTemplateUsed(response, 'Grades/modulestudent.html')


class GradesModulePartViewTest(TestCase):
    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        pk = ModulePart.objects.get(name='module_part0').pk

        self.client.logout()
        url = reverse('grades:module_part', kwargs={'pk': pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        pk = ModulePart.objects.get(name='module_part0').pk
        url = reverse('grades:module_part', kwargs={'pk': pk})

        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        pk = ModulePart.objects.get(name='module_part0').pk
        url = reverse('grades:module_part', kwargs={'pk': pk})

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
        pk = ModulePart.objects.get(name='module_part0').pk
        url = reverse('grades:module_part', kwargs={'pk': pk})
        user = User.objects.get(username='coordinator0')

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(url)

        self.assertEqual(response.resolver_match.func.__name__, ModulePartView.as_view().__name__)
        self.assertTemplateUsed(response, 'Grades/module_part.html')


class GradesTestViewTest(TestCase):
    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        pk = Test.objects.get(name='test0').pk

        self.client.logout()
        url = reverse('grades:test', kwargs={'pk': pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        pk = Test.objects.get(name='test0').pk
        url = reverse('grades:test', kwargs={'pk': pk})

        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        pk = Test.objects.get(name='test0').pk
        url = reverse('grades:test', kwargs={'pk': pk})

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
        pk = Test.objects.get(name='test0').pk
        url = reverse('grades:test', kwargs={'pk': pk})
        user = User.objects.get(username='coordinator0')

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(url)

        self.assertEqual(response.resolver_match.func.__name__, TestView.as_view().__name__)
        self.assertTemplateUsed(response, 'Grades/test.html')


class GetDataTest(TestCase):
    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        self.client.logout()
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk
        url = reverse("grades:get", kwargs={'pk': pk, 't': 'E'})
        response = self.client.get(url + "?view=mod_ed", follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url + "%3Fview%3Dmod_ed")

    def test_insufficient_permissions(self):
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk
        url = reverse("grades:get", kwargs={'pk': pk, 't': 'E'}) + "?view=mod_ed"
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk
        url = reverse("grades:get", kwargs={'pk': pk, 't': 'E'}) + "?view=mod_ed"

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

    def test_exams_mod_ed(self):
        pk = ModuleEdition.objects.get(module_code='001', year=timezone.now().year).pk
        url = reverse("grades:get", kwargs={'pk': pk, 't': 'E'}) + "?view=mod_ed"
        user = User.objects.get(username='coordinator0')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = OrderedDict()
        data['data'] = []
        di = OrderedDict()
        (m, qs) = create_grades_query('mod_ed', pk, user, 'E')
        for q in qs:
            key = "<a href={}>{} ({})</a>".format(
                reverse('grades:modstudent', kwargs={'pk': m.id, 'sid': q.person_id}),
                q.name, q.university_number)

            value = '<a id="grade_{}_{}"' \
                    'data-grade="{}"' \
                    'data-grade-min="{}" data-grade-max="{}"' \
                    'data-edit-url="{}" ' \
                    'data-remove-url="{}"' \
                    '>{}</a>'.format(q.person_id, q.test_id,
                                     (q.grade if q.grade else '-'),
                                     q.minimum_grade, q.maximum_grade,
                                     reverse('grades:edit', kwargs={'pk': q.test_id, 'sid': q.person_id}),
                                     reverse('grades:remove', kwargs={'pk': q.test_id, 'sid': q.person_id}),
                                     (q.grade if q.grade else '-'))

            if not key in di.keys():
                di[key] = []
            di[key].append(value)

        for key, values in di.items():
            data['data'].append([key] + values)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            data
        )


class EditDataTest(TestCase):
    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        self.client.logout()
        g = Grade.objects.get(grade=9)
        pk = g.test.pk
        s_pk = g.student.pk
        url_release = reverse("grades:bulk-release")
        url_edit = reverse("grades:edit", kwargs={'pk': pk, 'sid': s_pk})
        url_remove = reverse("grades:edit", kwargs={'pk': pk, 'sid': s_pk})

        response = self.client.post(url_release, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url_release)

        response = self.client.get(url_edit, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url_edit)

        response = self.client.get(url_remove, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url_remove)

    def test_permissions(self):
        g = Grade.objects.get(grade=9)
        pk = g.test.pk
        s_pk = g.student.pk
        url_release = reverse("grades:bulk-release")
        url_edit = reverse("grades:edit", kwargs={'pk': pk, 'sid': s_pk})
        url_remove = reverse("grades:edit", kwargs={'pk': pk, 'sid': s_pk})

        # ==== Login as teaching assistant ====
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))

        # Release
        response = self.client.post(url_release, {'tests': json.dumps([pk])})
        self.assertEqual(response.status_code, 403)

        # Edit
        response = self.client.get(url_edit)
        self.assertEqual(response.status_code, 200)

        # Remove
        response = self.client.get(url_remove)
        self.assertEqual(response.status_code, 200)

        # ==== Login as teacher ====
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))

        # Release
        response = self.client.post(url_release, {'tests': json.dumps([pk])})
        self.assertEqual(response.status_code, 403)

        # Edit
        response = self.client.get(url_edit)
        self.assertEqual(response.status_code, 200)

        # Remove
        response = self.client.get(url_remove)
        self.assertEqual(response.status_code, 200)

        # ==== Log in as coordinator =====
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))

        # Release
        response = self.client.post(url_release, {'tests': json.dumps([pk])})
        self.assertEqual(response.status_code, 200)

        # Edit
        response = self.client.get(url_edit)
        self.assertEqual(response.status_code, 200)

        # Remove
        response = self.client.get(url_remove)
        self.assertEqual(response.status_code, 200)

        # ==== Login as study adviser ====
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))

        # Release
        response = self.client.post(url_release, {'tests': json.dumps([pk])})
        self.assertEqual(response.status_code, 403)

        # Edit
        response = self.client.get(url_edit)
        self.assertEqual(response.status_code, 403)

        # Remove
        response = self.client.get(url_remove)
        self.assertEqual(response.status_code, 403)

        # ==== Login as student ====
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))

        # Release
        response = self.client.post(url_release, {'tests': json.dumps([pk])})
        self.assertEqual(response.status_code, 403)

        # Edit
        response = self.client.get(url_edit)
        self.assertEqual(response.status_code, 403)

        # Remove
        response = self.client.get(url_remove)
        self.assertEqual(response.status_code, 403)

    def test_release(self):
        pk = Test.objects.get(name='test0').pk
        url = reverse("grades:bulk-release")
        user = User.objects.get(username='coordinator0')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        # Check whether the test has already been released
        self.assertEqual(Test.objects.get(name='test0').released, False)

        # Release the test
        response = self.client.post(url, {'tests': json.dumps([pk])})

        # Check if a redirect happened and the test got released
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Test.objects.get(name='test0').released, True)

    def test_retract(self):
        pk = Test.objects.get(name='test0').pk
        url = reverse("grades:bulk-release")
        user = User.objects.get(username='coordinator0')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        # Check whether the test has already been released
        self.assertEqual(Test.objects.get(name='test0').released, False)

        # Release the test
        response = self.client.post(url, {'tests': json.dumps([pk])})

        # Check if a redirect happened and the test got released
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Test.objects.get(name='test0').released, True)

        # Retract the test
        response = self.client.post(url, {'tests': json.dumps([pk])})

        # Check if a redirect happened and if the test got retracted
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Test.objects.get(name='test0').released, False)

    def test_edit(self):
        g = Grade.objects.get(grade=9)
        pk = g.test.pk
        s_pk = g.student.pk
        url = reverse("grades:edit", kwargs={'pk': pk, 'sid': s_pk})
        user = User.objects.get(username='coordinator0')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        # Check whether the grade starts at a 9.0
        self.assertEqual(g.grade, 9.0)

        # Change the grade to a 5.5
        response = self.client.post(url, {'grade': '5.5'})

        # Check the response and see if the grade has changed
        self.assertEqual(response.status_code, 200)
        self.assertEqual((Grade.objects.filter(test=pk, student=s_pk).order_by('-id').first()).grade, 5.5)

    def test_remove(self):
        g = Grade.objects.get(grade=9)
        pk = g.test.pk
        s_pk = g.student.pk
        url = reverse("grades:remove", kwargs={'pk': pk, 'sid': s_pk})
        user = User.objects.get(username='coordinator0')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        # Check whether the grade starts at a 9.0
        self.assertEqual(g.grade, 9.0)

        # Remove the grade
        response = self.client.post(url)

        # Check the response and see if the grade has been removed
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(g, Grade.objects.filter(test=pk, student=s_pk))


class ExportDataTest(TestCase):
    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        self.client.logout()
        pk = Test.objects.get(name='test0').pk
        url = reverse("grades:export", kwargs={'pk': pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        pk = Test.objects.get(name='test0').pk
        url = reverse("grades:export", kwargs={'pk': pk})

        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

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

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        pk = Test.objects.get(name='test0').pk
        url = reverse("grades:export", kwargs={'pk': pk})

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
