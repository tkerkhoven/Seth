import json
from unittest import skipIf

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from Grades.models import Module, Person, Study, ModuleEdition, ModulePart, Studying, Test, Grade, Teacher, Coordinator
from Seth.settings import LOGIN_URL
from module_management.views import ModuleListView, ModuleDetailView, ModuleEditionDetailView, TestDetailView, ModuleEditionUpdateView, \
    ModulePartUpdateView, ModulePartDetailView, ModulePartDeleteView, TestDeleteView, TestUpdateView, ModuleEditionCreateView, \
    ModuleEditionCreateForm, ModulePartCreateView, TestCreateView, TestCreateForm

_RUN_QUERY_TESTS = False


def set_up_base_data():
    # Define Users
    dummy_user = User.objects.create(username='dummy_user', password='')

    student_user0 = User(username='student0', password='secure_password')
    student_user1 = User(username='student1', password='secure_password')
    student_user2 = User(username='student2', password='secure_password')
    teaching_assistant_user = User(username='teaching_assistant0', password='secure_password')
    teacher_user = User(username='teacher0', password='secure_password')
    teacher_user2 = User(username='teacher1', password='secure_password')
    study_adviser_user = User(username='study_adviser0', password='secure_password')
    coordinator_user = User(username='coordinator0', password='secure_password')
    coordinator_assistant_user = User(username='coordinator1', password='secure_password')
    student_user0.save()
    student_user1.save()
    student_user2.save()
    teaching_assistant_user.save()
    teacher_user.save()
    teacher_user2.save()
    study_adviser_user.save()
    coordinator_user.save()
    coordinator_assistant_user.save()

    # Define Persons
    student_person0 = Person(university_number='s0', name='Student 0', user=student_user0)
    student_person1 = Person(university_number='s5', name='Student 1', user=student_user1)
    student_person2 = Person(university_number='s6', name='Student 2', user=student_user2)
    teaching_assistant_person = Person(university_number='s1', name='Teaching Assistant 0', user=teaching_assistant_user)
    teacher_person = Person(university_number='m2', name='Teacher 0', user=teacher_user)
    teacher_person2 = Person(university_number='m8', name='Teacher 1', user=teacher_user2)
    study_adviser_person = Person(university_number='m3', name='Study Adviser 0', user=study_adviser_user)
    coordinator_person = Person(university_number='m4', name='Coordinator 0', user=coordinator_user)
    coordinator_assistant_person = Person(university_number='m5', name='Coordinator 1', user=coordinator_assistant_user)
    student_person0.save()
    student_person1.save()
    student_person2.save()
    teaching_assistant_person.save()
    teacher_person.save()
    teacher_person2.save()
    study_adviser_person.save()
    coordinator_person.save()
    coordinator_assistant_person.save()

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
    module_ed0 = ModuleEdition(module=module0, module_code='001', block='1A', year=timezone.now().year)
    module_ed0.save()

    module_ed1 = ModuleEdition(module=module0, module_code='001', block='1A', year=timezone.now().year - 2)
    module_ed1.save()

    module_ed2 = ModuleEdition(module=module1, module_code='002', block='1B', year=timezone.now().year)
    module_ed2.save()

    module_ed3 = ModuleEdition(module=module0, module_code='001', block='1A', year=timezone.now().year - 1)
    module_ed3.save()

    # Define Module Parts
    module_part0 = ModulePart(name='module_part0', module_edition=module_ed0)
    module_part0.save()

    module_part1 = ModulePart(name='module_part1', module_edition=module_ed1)
    module_part1.save()

    module_part2 = ModulePart(name='module_part2', module_edition=module_ed0)
    module_part2.save()

    # Define Studying
    studying0 = Studying(person=student_person0, module_edition=module_ed0, role='student')
    studying1 = Studying(person=student_person2, module_edition=module_ed0, role='student')
    studying2 = Studying(person=student_person1, module_edition=module_ed2, role='student')
    studying0.save()
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
    grade0 = Grade(test=test0, teacher=teacher_person, student=student_person0, description='grade0', grade=6)
    grade1 = Grade(test=test0, teacher=teacher_person, student=student_person1, description='grade0', grade=9)
    grade0.save()
    grade1.save()

    # Define Teachers
    teacher0 = Teacher(module_part=module_part0, person=teacher_person, role='T')
    teaching_assistant0 = Teacher(module_part=module_part0, person=teaching_assistant_person, role='A')
    teacher0.save()
    teaching_assistant0.save()
    teacher1 = Teacher(module_part=module_part1, person=teacher_person2, role='T')
    teacher1.save()

    # Define Coordinators
    coordinator0 = Coordinator(person=coordinator_person, module_edition=module_ed0, is_assistant=False)
    coordinator0.save()

    coordinator1 = Coordinator(person=coordinator_person, module_edition=module_ed3, is_assistant=False)
    coordinator1.save()

    coordinator2 = Coordinator(person=coordinator_assistant_person, module_edition=module_ed0, is_assistant=True)
    coordinator2.save()


def set_up_large_independent_data():
    for i in range(1000, 1100):
        # Define Users
        student_user0 = User(username='studentx' + str(i), password='secure_password')
        student_user1 = User(username='studenty' + str(i), password='secure_password')
        teaching_assistant_user = User(username='teaching_assistant' + str(i), password='secure_password')
        teacher_user = User(username='teacher' + str(i), password='secure_password')
        study_adviser_user = User(username='study_adviser' + str(i), password='secure_password')
        coordinator_user = User(username='coordinator' + str(i), password='secure_password')
        student_user0.save()
        student_user1.save()
        teaching_assistant_user.save()
        teacher_user.save()
        study_adviser_user.save()
        coordinator_user.save()

        # Define Persons
        student_person0 = Person(university_number='sx' + str(i), name='Studentx ' + str(i), user=student_user0)
        student_person1 = Person(university_number='sy' + str(i), name='Studenty ' + str(i), user=student_user1)
        teaching_assistant_person = Person(university_number='sz' + str(i), name='Teaching Assistant ' + str(i), user=teaching_assistant_user)
        teacher_person = Person(university_number='mx' + str(i), name='Teacher ' + str(i), user=teacher_user)
        study_adviser_person = Person(university_number='my' + str(i), name='Study Adviser ' + str(i), user=study_adviser_user)
        coordinator_person = Person(university_number='mz' + str(i), name='Coordinator ' + str(i), user=coordinator_user)
        student_person0.save()
        student_person1.save()
        teaching_assistant_person.save()
        teacher_person.save()
        study_adviser_person.save()
        coordinator_person.save()

        # Define Modules
        module0 = Module(name='Module x' + str(i))
        module0.save()

        module1 = Module(name='Module y' + str(i))
        module1.save()

        # Define Study
        study = Study(abbreviation='STU' + str(i), name='Study ' + str(i))
        study.save()
        study.advisers.add(study_adviser_person)
        study.modules.add(module0)

        # Define Module Editions
        module_ed0 = ModuleEdition(module=module0, module_code='x' + str(i), block='1A', year=timezone.now().year)
        module_ed0.save()

        module_ed1 = ModuleEdition(module=module0, module_code='x' + str(i), block='1A', year=timezone.now().year - 2)
        module_ed1.save()

        module_ed2 = ModuleEdition(module=module1, module_code='y' + str(i), block='1B', year=timezone.now().year)
        module_ed2.save()

        module_ed3 = ModuleEdition(module=module0, module_code='x' + str(i), block='1A', year=timezone.now().year - 1)
        module_ed3.save()

        # Define Module Parts
        module_part0 = ModulePart(name='module_partx' + str(i), module_edition=module_ed0)
        module_part0.save()

        module_part1 = ModulePart(name='module_party' + str(i), module_edition=module_ed1)
        module_part1.save()

        module_part2 = ModulePart(name='module_partz' + str(i), module_edition=module_ed0)
        module_part2.save()

        # Define Studying
        studying = Studying(person=student_person0, module_edition=module_ed0, role='student')
        studying.save()

        # Define Tests
        test0 = Test(module_part=module_part0, name='testx' + str(i), type='E')
        test0.save()

        test1 = Test(module_part=module_part1, name='testy' + str(i), type='P')
        test1.save()

        test2 = Test(module_part=module_part2, name='testz' + str(i), type='A')
        test2.save()

        # Define Grades
        grade0 = Grade(test=test0, teacher=teacher_person, student=student_person0, description='gradex' + str(i), grade=6)
        grade1 = Grade(test=test0, teacher=teacher_person, student=student_person1, description='gradey' + str(i), grade=9)
        grade0.save()
        grade1.save()

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


def set_up_large_dependent_data():
    old_module = Module.objects.get(name='Module 1')
    old_module_edition = ModuleEdition.objects.get(module=old_module.pk, block='1A', year=timezone.now().year)
    old_module_part = ModulePart.objects.get(module_edition=old_module_edition.pk, name='module_part0')
    old_test = Test.objects.get(module_part=old_module_part.pk, name='test0', type='E')
    old_study = Study.objects.get(abbreviation='STU', name='Study')

    for i in range(100):
        # Define Users
        student_user0 = User(username='studentq' + str(i), password='secure_password')
        teaching_assistant_user = User(username='teaching_assistantq' + str(i), password='secure_password')
        teacher_user = User(username='teacherq' + str(i), password='secure_password')
        study_adviser_user = User(username='study_adviserq' + str(i), password='secure_password')
        coordinator_user = User(username='coordinatorq' + str(i), password='secure_password')
        student_user0.save()
        teaching_assistant_user.save()
        teacher_user.save()
        study_adviser_user.save()
        coordinator_user.save()

        # Define Persons
        student_person0 = Person(university_number='sxq' + str(i), name='Student q' + str(i), user=student_user0)
        teaching_assistant_person = Person(university_number='szq' + str(i), name='Teaching Assistant q' + str(i), user=teaching_assistant_user)
        teacher_person = Person(university_number='mxq' + str(i), name='Teacher q' + str(i), user=teacher_user)
        study_adviser_person = Person(university_number='myq' + str(i), name='Study Adviser q' + str(i), user=study_adviser_user)
        coordinator_person = Person(university_number='mzq' + str(i), name='Coordinator q' + str(i), user=coordinator_user)
        student_person0.save()
        teaching_assistant_person.save()
        teacher_person.save()
        study_adviser_person.save()
        coordinator_person.save()

        # Define Modules
        module0 = Module(name='Module xq' + str(i))
        module0.save()

        # Fill old_study
        old_study.advisers.add(study_adviser_person)
        old_study.modules.add(module0)

        # Define Module Editions / Fill old_module
        module_ed0 = ModuleEdition(module=old_module, module_code='xq' + str(i), block='1A', year=i)
        module_ed0.save()

        # Define Module Parts / Fill old_module_edition
        module_part0 = ModulePart(name='module_partxq' + str(i), module_edition=old_module_edition)
        module_part0.save()

        # Define Studying / Fill old_module_ed, old_study
        studying = Studying(person=student_person0, module_edition=old_module_edition, role='student')
        studying.save()

        # Define Tests / Fill old_module_part
        test0 = Test(module_part=old_module_part, name='testxq' + str(i), type='E')
        test0.save()

        # Define Grades / Fill old_test
        grade0 = Grade(test=old_test, teacher=teacher_person, student=student_person0, description='gradexq' + str(i), grade=6)
        grade0.save()

        # Define Teachers / Fill old_module_part
        teacher0 = Teacher(module_part=old_module_part, person=teacher_person, role='T')
        teaching_assistant0 = Teacher(module_part=old_module_part, person=teaching_assistant_person, role='A')
        teacher0.save()
        teaching_assistant0.save()

        # Define Coordinators
        coordinator0 = Coordinator(person=coordinator_person, module_edition=old_module_edition, is_assistant=False)
        coordinator0.save()


def get_list_from_queryset(queryset):
    return [repr(r) for r in queryset]


class ModuleManagementModuleListTests(TestCase):
    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        self.client.logout()
        url = reverse('module_management:module_overview')
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        url = reverse('module_management:module_overview')

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
        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(reverse('module_management:module_overview'))
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        user = User.objects.get(username='coordinator0')

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(reverse('module_management:module_overview'))

        self.assertEqual(response.resolver_match.func.__name__, ModuleListView.as_view().__name__)
        self.assertTemplateUsed(response, 'module_management/module_overview.html')

        self.assertQuerysetEqual(response.context['module_list'],
                                 get_list_from_queryset(Module.objects.filter(moduleedition__coordinators__user=user).distinct()))
        self.assertQuerysetEqual(response.context['mod_eds'], get_list_from_queryset(ModuleEdition.objects.filter(coordinators__user=user)))

        self.assertContains(response, 'Module 1')
        self.assertContains(response, '{}-{}-{}'.format(timezone.now().year, '001', '1A'))
        self.assertContains(response, '{}-{}-{}'.format(timezone.now().year - 1, '001', '1A'))
        self.assertNotContains(response, '{}-{}-{}'.format(timezone.now().year - 2, '001', '1A'))
        self.assertNotContains(response, 'Module 2')
        self.assertNotContains(response, '{}-{}-{}'.format(timezone.now().year, '002', '1B'))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        user = User.objects.get(username='coordinator0')
        url_1 = reverse('module_management:module_overview')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(7):
            self.client.get(url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        user = User.objects.get(username='coordinator0')
        url_1 = reverse('module_management:module_overview')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(7):
            self.client.get(url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        user = User.objects.get(username='coordinator0')
        url_1 = reverse('module_management:module_overview')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(7):
            self.client.get(url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        user = User.objects.get(username='coordinator0')
        url_1 = reverse('module_management:module_overview')

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(7):
            self.client.get(url_1, follow=True)


class ModuleManagementModuleDetailTests(TestCase):
    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        pk = Module.objects.get(name='Module 1').pk

        self.client.logout()
        url = reverse('module_management:module_detail', kwargs={'pk': pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        pk_1 = Module.objects.get(name='Module 1').pk
        pk_2 = Module.objects.get(name='Module 2').pk

        url_1 = reverse('module_management:module_detail', kwargs={'pk': pk_1})
        url_2 = reverse('module_management:module_detail', kwargs={'pk': pk_2})

        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(url_1)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(url_1)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(url_1)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(url_1)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(url_2)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        pk_1 = Module.objects.get(name='Module 1').pk

        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk_1}))
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        user = User.objects.get(username='coordinator0')
        pk = Module.objects.get(name='Module 1').pk

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk}))

        self.assertEqual(response.resolver_match.func.__name__, ModuleDetailView.as_view().__name__)
        self.assertTemplateUsed(response, 'module_management/module_detail.html')

        self.assertEqual(response.context['module'], Module.objects.get(pk=pk))
        self.assertQuerysetEqual(response.context['module_editions'], get_list_from_queryset(ModuleEdition.objects.filter(coordinators__user=user)))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        user = User.objects.get(username='coordinator0')
        pk_1 = Module.objects.get(name='Module 1').pk
        url_1 = reverse('module_management:module_detail', kwargs={'pk': pk_1})

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(8):
            self.client.get(url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        user = User.objects.get(username='coordinator0')
        pk_1 = Module.objects.get(name='Module 1').pk
        url_1 = reverse('module_management:module_detail', kwargs={'pk': pk_1})

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(8):
            self.client.get(url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        user = User.objects.get(username='coordinator0')
        pk_1 = Module.objects.get(name='Module 1').pk
        url_1 = reverse('module_management:module_detail', kwargs={'pk': pk_1})

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(8):
            self.client.get(url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        user = User.objects.get(username='coordinator0')
        pk_1 = Module.objects.get(name='Module 1').pk
        url_1 = reverse('module_management:module_detail', kwargs={'pk': pk_1})

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(8):
            self.client.get(url_1, follow=True)


class ModuleManagementModuleEditionDetailTests(TestCase):
    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        mod_1 = Module.objects.get(name='Module 1').pk
        pk = ModuleEdition.objects.get(module=mod_1, block='1A', year=timezone.now().year).pk

        self.client.logout()
        url = reverse('module_management:module_edition_detail', kwargs={'pk': pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        mod_1 = Module.objects.get(name='Module 1').pk
        mod_2 = Module.objects.get(name='Module 2').pk
        pk_1 = ModuleEdition.objects.get(module=mod_1, block='1A', year=timezone.now().year).pk
        pk_2 = ModuleEdition.objects.get(module=mod_1, block='1A', year=timezone.now().year - 2).pk
        pk_3 = ModuleEdition.objects.get(module=mod_2, block='1B', year=timezone.now().year).pk
        url_1 = reverse('module_management:module_edition_detail', kwargs={'pk': pk_1})
        url_2 = reverse('module_management:module_edition_detail', kwargs={'pk': pk_2})
        url_3 = reverse('module_management:module_edition_detail', kwargs={'pk': pk_3})

        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(url_1)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(url_1)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(url_1)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(url_1)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(url_2)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(url_3)
        self.assertEqual(response.status_code, 403)

    def test_contents(self):
        user = User.objects.get(username='coordinator0')
        mod_1 = Module.objects.get(name='Module 1').pk
        module_edition = ModuleEdition.objects.get(module=mod_1, block='1A', year=timezone.now().year).pk
        url = reverse('module_management:module_edition_detail', kwargs={'pk': module_edition})

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, ModuleEditionDetailView.as_view().__name__)
        self.assertTemplateUsed(response, 'module_management/module_edition_detail.html')

        self.assertEqual(response.context['moduleedition'], ModuleEdition.objects.get(pk=module_edition))
        self.assertQuerysetEqual(response.context['studying'], get_list_from_queryset(Studying.objects.filter(module_edition=module_edition)))
        self.assertQuerysetEqual(response.context['module_parts'], get_list_from_queryset(ModulePart.objects.filter(module_edition=module_edition)))
        self.assertQuerysetEqual(response.context['coordinators'], get_list_from_queryset(Coordinator.objects.filter(module_edition=module_edition)))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        user = User.objects.get(username='coordinator0')
        mod_1 = Module.objects.get(name='Module 1').pk
        pk_1 = ModuleEdition.objects.get(module=mod_1, block='1A', year=timezone.now().year).pk
        url_1 = reverse('module_management:module_edition_detail', kwargs={'pk': pk_1})

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(12):
            self.client.get(url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        user = User.objects.get(username='coordinator0')
        mod_1 = Module.objects.get(name='Module 1').pk
        pk_1 = ModuleEdition.objects.get(module=mod_1, block='1A', year=timezone.now().year).pk
        url_1 = reverse('module_management:module_edition_detail', kwargs={'pk': pk_1})

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(12):
            self.client.get(url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        user = User.objects.get(username='coordinator0')
        mod_1 = Module.objects.get(name='Module 1').pk
        pk_1 = ModuleEdition.objects.get(module=mod_1, block='1A', year=timezone.now().year).pk
        url_1 = reverse('module_management:module_edition_detail', kwargs={'pk': pk_1})

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(12):
            self.client.get(url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        user = User.objects.get(username='coordinator0')
        mod_1 = Module.objects.get(name='Module 1').pk
        pk_1 = ModuleEdition.objects.get(module=mod_1, block='1A', year=timezone.now().year).pk
        url_1 = reverse('module_management:module_edition_detail', kwargs={'pk': pk_1})

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(12):
            self.client.get(url_1, follow=True)


class ModuleManagementModuleEditionUpdateFormTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:module_edition_update'
        self.model_cls = ModuleEdition
        mod_1 = Module.objects.get(name='Module 1').pk
        self.pk_1 = self.model_cls.objects.get(module=mod_1, block='1A', year=timezone.now().year).pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.user = User.objects.get(username='coordinator0')

    def test_fields_required(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1, {})
        self.assertFormError(response, 'form', 'year', 'This field is required.')
        self.assertFormError(response, 'form', 'block', 'This field is required.')

    def test_protected_fields(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        self.client.post(self.url_1,
                         {'year': 2020, 'block': '1A', 'module': Module.objects.get(name='Module 2').pk})
        self.assertEqual('001', ModuleEdition.objects.get(year=2020).module_code)

    def test_invalid_input_year(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1, {'year': 'a', 'block': '1A'})
        self.assertFormError(response, 'form', 'year', 'Enter a whole number.')
        response = self.client.post(self.url_1, {'year': 2017.2, 'block': '1A'})
        self.assertFormError(response, 'form', 'year', 'Enter a whole number.')

    def test_invalid_input_block(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1C'})
        self.assertFormError(response, 'form', 'block', 'Select a valid choice. 1C is not one of the available choices.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1'})
        self.assertFormError(response, 'form', 'block', 'Select a valid choice. 1 is not one of the available choices.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': 1})
        self.assertFormError(response, 'form', 'block', 'Select a valid choice. 1 is not one of the available choices.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': 'Block 1A'})
        self.assertFormError(response, 'form', 'block', 'Select a valid choice. Block 1A is not one of the available choices.')


class ModuleManagementModuleEditionUpdateTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:module_edition_update'
        self.template = 'module_management/module_edition_update.html'
        self.view_cls = ModuleEditionUpdateView
        self.model_cls = ModuleEdition
        self.model_name = 'moduleedition'
        mod_1 = Module.objects.get(name='Module 1').pk
        self.pk_1 = self.model_cls.objects.get(module=mod_1, block='1A', year=timezone.now().year).pk
        self.pk_2 = self.model_cls.objects.get(module=mod_1, block='1A', year=timezone.now().year - 2).pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.url_2 = reverse(self.base_url, kwargs={'pk': self.pk_2})
        self.user = User.objects.get(username='coordinator0')

    def test_no_login(self):
        self.client.logout()
        response = self.client.get(self.url_1, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + self.url_1)

    def test_insufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.get(self.url_1, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, self.view_cls.as_view().__name__)
        self.assertTemplateUsed(response, self.template)

        self.assertEqual(response.context[self.model_name], self.model_cls.objects.get(pk=self.pk_1))

    def test_update(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        self.assertTrue(ModuleEdition.objects.filter(year=timezone.now().year, block='1A'))
        self.client.post(self.url_1, {'year': 2020, 'block': '1A'})
        self.assertFalse(ModuleEdition.objects.filter(year=timezone.now().year, block='1A'))
        self.assertTrue(ModuleEdition.objects.filter(year=2020))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(7):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(8):
            self.client.post(self.url_1, {'year': 2020, 'block': '1A'})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(7):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(8):
            self.client.post(self.url_1, {'year': 2020, 'block': '1A'})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(7):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(8):
            self.client.post(self.url_1, {'year': 2020, 'block': '1A'})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(7):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(8):
            self.client.post(self.url_1, {'year': 2020, 'block': '1A'})


class ModuleManagementModuleEditionCreateTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:module_edition_create'
        self.template = 'module_management/module_edition_create.html'
        self.view_cls = ModuleEditionCreateView
        self.model_cls = ModuleEdition
        self.model_name = 'moduleedition'
        self.super_cls = Module
        self.form_cls = ModuleEditionCreateForm
        self.pk_1 = self.super_cls.objects.get(name='Module 1').pk
        self.pk_2 = self.super_cls.objects.get(name='Module 2').pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.url_2 = reverse(self.base_url, kwargs={'pk': self.pk_2})
        self.user = User.objects.get(username='coordinator0')

    def test_no_login(self):
        self.client.logout()
        response = self.client.get(self.url_1, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + self.url_1)

    def test_insufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.get(self.url_1, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, self.view_cls.as_view().__name__)
        self.assertTemplateUsed(response, self.template)

        self.assertEqual(response.context['form'].__class__, self.form_cls)

    def test_creation(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        self.assertFalse(self.model_cls.objects.filter(year=1337, block='2B', module=self.pk_1))
        self.client.post(self.url_1, {'year': 1337, 'block': '2B'})
        self.assertTrue(self.model_cls.objects.filter(year=1337, block='2B', module=self.pk_1))

        new_object = self.model_cls.objects.get(year=1337, block='2B', module=self.pk_1)
        self.assertEquals(self.pk_1, new_object.module.pk)
        self.assertEquals(1337, new_object.year)
        self.assertEquals('2B', new_object.block)

        self.assertEqual(2, len(ModulePart.objects.filter(module_edition=new_object.pk)))
        self.assertEqual(2, len(Test.objects.filter(module_part__module_edition=new_object.pk)))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(31):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(30):
            self.client.post(self.url_1, {'year': 1337, 'block': '2B', })

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(31):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(30):
            self.client.post(self.url_1, {'year': 1337, 'block': '2B'})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(11):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(30):
            self.client.post(self.url_1, {'year': 1337, 'block': '2B'})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(11):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(30):
            self.client.post(self.url_1, {'year': 1337, 'block': '2B'})


class ModuleManagementModulePartDetailTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:module_part_detail'
        self.template = 'module_management/module_part_detail.html'
        self.view_cls = ModulePartDetailView
        self.model_cls = ModulePart
        self.model_name = 'modulepart'
        self.pk_1 = self.model_cls.objects.get(name='module_part0').pk
        self.pk_2 = self.model_cls.objects.get(name='module_part1').pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.url_2 = reverse(self.base_url, kwargs={'pk': self.pk_2})
        self.user = User.objects.get(username='coordinator0')

    def test_no_login(self):
        self.client.logout()
        response = self.client.get(self.url_1, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + self.url_1)

    def test_insufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.get(self.url_1, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, self.view_cls.as_view().__name__)
        self.assertTemplateUsed(response, self.template)

        self.assertEqual(response.context[self.model_name], self.model_cls.objects.get(pk=self.pk_1))
        self.assertQuerysetEqual(response.context['studying'], get_list_from_queryset(
            Studying.objects.filter(module_edition=ModulePart.objects.get(pk=self.pk_1).module_edition.pk)))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(14):
            self.client.get(self.url_1)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(14):
            self.client.get(self.url_1)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(14):
            self.client.get(self.url_1)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(14):
            self.client.get(self.url_1)


class ModuleManagementModulePartUpdateFormTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:module_part_update'
        self.model_cls = ModulePart
        self.pk_1 = self.model_cls.objects.get(name='module_part0').pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.user = User.objects.get(username='coordinator0')

    def test_fields_required(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1, {})
        self.assertFormError(response, 'form', 'name', 'This field is required.')
        self.assertFormError(response, 'form', 'teachers', 'This field is required.')

    def test_protected_fields(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        self.client.post(self.url_1,
                         {'name': 'newname', 'teachers': {}, 'module_edition': ModuleEdition.objects.get(year=timezone.now().year - 2).pk})
        self.assertEqual(ModuleEdition.objects.get(year=timezone.now().year, block='1A').pk, ModulePart.objects.get(pk=self.pk_1).module_edition.pk)

    def test_invalid_input_name(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        s = ''
        for i in range(256):
            s = s + str(i)
        response = self.client.post(self.url_1, {'name': s, 'teachers': {}})
        self.assertFormError(response, 'form', 'name', 'Ensure this value has at most 255 characters (it has 658).')

    def test_invalid_input_teachers(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1, {'name': 'newname', 'teachers': {12345}})
        self.assertFormError(response, 'form', 'teachers', 'Select a valid choice. 12345 is not one of the available choices.')


class ModuleManagementModulePartUpdateTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:module_part_update'
        self.template = 'module_management/module_part_update.html'
        self.view_cls = ModulePartUpdateView
        self.model_cls = ModulePart
        self.model_name = 'modulepart'
        self.pk_1 = self.model_cls.objects.get(name='module_part0').pk
        self.pk_2 = self.model_cls.objects.get(name='module_part1').pk
        self.pk_3 = self.model_cls.objects.get(name='module_part2').pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.url_2 = reverse(self.base_url, kwargs={'pk': self.pk_2})
        self.url_3 = reverse(self.base_url, kwargs={'pk': self.pk_3})
        self.user = User.objects.get(username='coordinator0')
        self.person1 = Person.objects.get(university_number='s1').pk
        self.person2 = Person.objects.get(university_number='m2').pk

    def test_no_login(self):
        self.client.logout()
        response = self.client.get(self.url_1, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + self.url_1)

    def test_insufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.get(self.url_1, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, self.view_cls.as_view().__name__)
        self.assertTemplateUsed(response, self.template)

        self.assertEqual(response.context[self.model_name], self.model_cls.objects.get(pk=self.pk_1))

    def test_update(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        self.assertTrue(ModulePart.objects.filter(name='module_part2'))
        self.client.post(self.url_3, {'name': 'module_part2_new', 'teachers': (self.person1, self.person2)})
        self.assertFalse(ModulePart.objects.filter(name='module_part2'))
        self.assertTrue(ModulePart.objects.filter(name='module_part2_new'))
        self.assertTrue(Teacher.objects.filter(role='A', person=self.person1, module_part=self.pk_3))
        self.assertTrue(Teacher.objects.filter(role='T', person=self.person2, module_part=self.pk_3))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(9):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(10):
            self.client.post(self.url_3, {'name': 'module_part2_new', 'teachers': (self.person1, self.person2)})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(9):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(10):
            self.client.post(self.url_3, {'name': 'module_part2_new', 'teachers': (self.person1, self.person2)})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(9):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(10):
            self.client.post(self.url_3, {'name': 'module_part2_new', 'teachers': (self.person1, self.person2)})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(9):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(10):
            self.client.post(self.url_3, {'name': 'module_part2_new', 'teachers': (self.person1, self.person2)})


class ModuleManagementModulePartCreateTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:module_part_create'
        self.template = 'module_management/module_part_create.html'
        self.view_cls = ModulePartCreateView
        self.model_cls = ModulePart
        self.model_name = 'modulepart'
        self.super_cls = ModuleEdition
        mod_1 = Module.objects.get(name='Module 1').pk
        self.pk_1 = self.super_cls.objects.get(module=mod_1, block='1A', year=timezone.now().year).pk
        self.pk_2 = self.super_cls.objects.get(module=mod_1, block='1A', year=timezone.now().year - 2).pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.url_2 = reverse(self.base_url, kwargs={'pk': self.pk_2})
        self.user = User.objects.get(username='coordinator0')
        self.person1 = Person.objects.get(university_number='s1').pk
        self.person2 = Person.objects.get(university_number='m2').pk

    def test_no_login(self):
        self.client.logout()
        response = self.client.get(self.url_1, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + self.url_1)

    def test_insufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.get(self.url_1, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, self.view_cls.as_view().__name__)
        self.assertTemplateUsed(response, self.template)

    def test_creation(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        self.assertFalse(self.model_cls.objects.filter(name='new_object'))
        self.client.post(self.url_1, {'name': 'new_object', 'teachers': (self.person1, self.person2)})
        self.assertTrue(self.model_cls.objects.filter(name='new_object'))

        new_object = self.model_cls.objects.get(name='new_object')
        self.assertEquals(self.pk_1, new_object.module_edition.pk)
        self.assertEquals('new_object', new_object.name)
        self.assertTrue(Teacher.objects.filter(role='A', person=self.person1, module_part=new_object.pk))
        self.assertTrue(Teacher.objects.filter(role='T', person=self.person2, module_part=new_object.pk))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(7):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(16):
            self.client.post(self.url_1, {'name': 'new_object', 'teachers': (self.person1, self.person2)})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(7):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(16):
            self.client.post(self.url_1, {'name': 'new_object', 'teachers': (self.person1, self.person2)})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(7):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(16):
            self.client.post(self.url_1, {'name': 'new_object', 'teachers': (self.person1, self.person2)})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(7):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(16):
            self.client.post(self.url_1, {'name': 'new_object', 'teachers': (self.person1, self.person2)})


class ModuleManagementModulePartDeleteTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:module_part_delete'
        self.template = 'module_management/module_part_delete.html'
        self.view_cls = ModulePartDeleteView
        self.model_cls = ModulePart
        self.model_name = 'modulepart'
        self.pk_1 = self.model_cls.objects.get(name='module_part0').pk
        self.pk_2 = self.model_cls.objects.get(name='module_part1').pk
        self.pk_3 = self.model_cls.objects.get(name='module_part2').pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.url_2 = reverse(self.base_url, kwargs={'pk': self.pk_2})
        self.url_3 = reverse(self.base_url, kwargs={'pk': self.pk_3})
        self.redirect_url = reverse('module_management:module_overview')
        self.user = User.objects.get(username='coordinator0')

    def test_no_login(self):
        self.client.logout()
        response = self.client.get(self.url_1, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + self.url_1)

    def test_insufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

    def test_insufficient_permissions_deletion_with_grades(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_3)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.get(self.url_3, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, self.view_cls.as_view().__name__)
        self.assertTemplateUsed(response, self.template)

        self.assertEqual(response.context[self.model_name], self.model_cls.objects.get(pk=self.pk_3))

    def test_deletion(self):
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_3, follow=True)

        self.assertRedirects(response, self.redirect_url)
        self.assertFalse(Test.objects.filter(pk=self.pk_3))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(8):
            self.client.get(self.url_3)

        with self.assertNumQueries(10):
            self.client.post(self.url_3)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(8):
            self.client.get(self.url_3)

        with self.assertNumQueries(10):
            self.client.post(self.url_3)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(8):
            self.client.get(self.url_3)

        with self.assertNumQueries(10):
            self.client.post(self.url_3)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(8):
            self.client.get(self.url_3)

        with self.assertNumQueries(10):
            self.client.post(self.url_3)


class ModuleManagementTestDetailTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:test_detail'
        self.pk_1 = Test.objects.get(name='test0').pk
        self.pk_2 = Test.objects.get(name='test1').pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.url_2 = reverse(self.base_url, kwargs={'pk': self.pk_2})
        self.user = User.objects.get(username='coordinator0')
        self.model_cls = Test
        self.view_cls = TestDetailView
        self.template = 'module_management/test_detail.html'
        self.model_name = 'test'

    def test_no_login(self):
        self.client.logout()
        response = self.client.get(self.url_1, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + self.url_1)

    def test_insufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.get(self.url_1, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, self.view_cls.as_view().__name__)
        self.assertTemplateUsed(response, self.template)

        self.assertEqual(response.context[self.model_name], self.model_cls.objects.get(pk=self.pk_1))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(8):
            self.client.get(self.url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(8):
            self.client.get(self.url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(8):
            self.client.get(self.url_1, follow=True)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(8):
            self.client.get(self.url_1, follow=True)


class ModuleManagementTestUpdateFormTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:test_update'
        self.model_cls = Test
        self.pk_1 = self.model_cls.objects.get(name='test0').pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.user = User.objects.get(username='coordinator0')

    def test_fields_required(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1, {})
        self.assertFormError(response, 'form', 'type', 'This field is required.')
        self.assertFormError(response, 'form', 'maximum_grade', 'This field is required.')
        self.assertFormError(response, 'form', 'minimum_grade', 'This field is required.')

    def test_protected_fields(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        self.client.post(self.url_1,
                         {'name': 'newname', 'type': 'E', 'maximum_grade': 10, 'minimum_grade': 1,
                          'module_part': ModulePart.objects.get(name='module_part1').pk})
        self.assertEqual(Test.objects.get(pk=self.pk_1).module_part.pk, ModulePart.objects.get(name='module_part0').pk)

    def test_invalid_input_name(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        s = ''
        for i in range(256):
            s = s + str(i)
        response = self.client.post(self.url_1, {'name': s, 'type': 'E', 'maximum_grade': 10, 'minimum_grade': 1})
        self.assertFormError(response, 'form', 'name', 'Ensure this value has at most 255 characters (it has 658).')

    def test_invalid_input_type(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'Exam', 'maximum_grade': 10, 'minimum_grade': 1})
        self.assertFormError(response, 'form', 'type', 'Select a valid choice. Exam is not one of the available choices.')
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'X', 'maximum_grade': 10, 'minimum_grade': 1})
        self.assertFormError(response, 'form', 'type', 'Select a valid choice. X is not one of the available choices.')
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 0, 'maximum_grade': 10, 'minimum_grade': 1})
        self.assertFormError(response, 'form', 'type', 'Select a valid choice. 0 is not one of the available choices.')

    def test_invalid_input_maximum_grade(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'E', 'maximum_grade': 100000, 'minimum_grade': 1})
        self.assertFormError(response, 'form', 'maximum_grade', 'Ensure that there are no more than 4 digits in total.')
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'E', 'maximum_grade': 'Ten', 'minimum_grade': 1})
        self.assertFormError(response, 'form', 'maximum_grade', 'Enter a number.')

    def test_invalid_input_minimum_grade(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'E', 'minimum_grade': 100000, 'maximum_grade': 1})
        self.assertFormError(response, 'form', 'minimum_grade', 'Ensure that there are no more than 4 digits in total.')
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'E', 'minimum_grade': 'Ten', 'maximum_grade': 1})
        self.assertFormError(response, 'form', 'minimum_grade', 'Enter a number.')


class ModuleManagementTestUpdateTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:test_update'
        self.template = 'module_management/test_update.html'
        self.view_cls = TestUpdateView
        self.model_cls = Test
        self.model_name = 'test'
        self.pk_1 = self.model_cls.objects.get(name='test0').pk
        self.pk_2 = self.model_cls.objects.get(name='test1').pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.url_2 = reverse(self.base_url, kwargs={'pk': self.pk_2})
        self.user = User.objects.get(username='coordinator0')

    def test_no_login(self):
        self.client.logout()
        response = self.client.get(self.url_1, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + self.url_1)

    def test_insufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.get(self.url_1, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, self.view_cls.as_view().__name__)
        self.assertTemplateUsed(response, self.template)

        self.assertEqual(response.context[self.model_name], self.model_cls.objects.get(pk=self.pk_1))

    def test_update(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        self.assertTrue(Test.objects.filter(name='test0'))
        self.client.post(self.url_1, {'name': 'test0_new', 'type': 'P', 'maximum_grade': '1', 'minimum_grade': '10'})
        self.assertFalse(Test.objects.filter(name='test0'))
        self.assertTrue(Test.objects.filter(name='test0_new'))
        self.assertEquals('P', Test.objects.get(pk=self.pk_1).type)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(5):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(5):
            self.client.post(self.url_1,
                             {'name': 'test0_new', 'type': 'P', 'time': '2017-10-11 13:37:00', 'maximum_grade': '1', 'minimum_grade': '10'})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(5):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(5):
            self.client.post(self.url_1,
                             {'name': 'test0_new', 'type': 'P', 'time': '2017-10-11 13:37:00', 'maximum_grade': '1', 'minimum_grade': '10'})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(5):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(5):
            self.client.post(self.url_1,
                             {'name': 'test0_new', 'type': 'P', 'time': '2017-10-11 13:37:00', 'maximum_grade': '1', 'minimum_grade': '10'})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(5):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(5):
            self.client.post(self.url_1,
                             {'name': 'test0_new', 'type': 'P', 'maximum_grade': '1', 'minimum_grade': '10'})


class ModuleManagementTestCreateTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:test_create'
        self.template = 'module_management/test_create.html'
        self.view_cls = TestCreateView
        self.model_cls = Test
        self.model_name = 'test'
        self.super_cls = ModulePart
        self.form_cls = TestCreateForm
        self.pk_1 = self.super_cls.objects.get(name='module_part0').pk
        self.pk_2 = self.super_cls.objects.get(name='module_part1').pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.url_2 = reverse(self.base_url, kwargs={'pk': self.pk_2})
        self.user = User.objects.get(username='coordinator0')

    def test_no_login(self):
        self.client.logout()
        response = self.client.get(self.url_1, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + self.url_1)

    def test_insufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.get(self.url_1, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, self.view_cls.as_view().__name__)
        self.assertTemplateUsed(response, self.template)

        self.assertEqual(response.context['form'].__class__, self.form_cls)

    def test_creation(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        self.assertFalse(self.model_cls.objects.filter(name='new_object'))
        self.client.post(self.url_1, {'name': 'new_object', 'type': 'P', 'minimum_grade': 42, 'maximum_grade': 133.7})
        self.assertTrue(self.model_cls.objects.filter(name='new_object'))

        new_object = self.model_cls.objects.get(name='new_object')
        self.assertEquals(self.pk_1, new_object.module_part.pk)
        self.assertEquals('new_object', new_object.name)
        self.assertEquals('P', new_object.type)
        self.assertEquals(42, float(new_object.minimum_grade))
        self.assertEquals(133.7, float(new_object.maximum_grade))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(15):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(9):
            self.client.post(self.url_1,
                             {'name': 'new_object', 'type': 'A', 'minimum_grade': 42, 'maximum_grade': 133.7})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(15):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(9):
            self.client.post(self.url_1,
                             {'name': 'new_object', 'type': 'A', 'minimum_grade': 42, 'maximum_grade': 133.7})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(15):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(9):
            self.client.post(self.url_1,
                             {'name': 'new_object', 'type': 'A', 'minimum_grade': 42, 'maximum_grade': 133.7})

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(15):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(9):
            self.client.post(self.url_1,
                             {'name': 'new_object', 'type': 'A', 'minimum_grade': 42, 'maximum_grade': 133.7})


class ModuleManagementTestDeleteTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:test_delete'
        self.template = 'module_management/test_delete.html'
        self.view_cls = TestDeleteView
        self.model_cls = Test
        self.model_name = 'test'
        self.pk_1 = self.model_cls.objects.get(name='test0').pk
        self.pk_2 = self.model_cls.objects.get(name='test1').pk
        self.pk_3 = self.model_cls.objects.get(name='test2').pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.url_2 = reverse(self.base_url, kwargs={'pk': self.pk_2})
        self.url_3 = reverse(self.base_url, kwargs={'pk': self.pk_3})
        self.redirect_url = reverse('module_management:module_overview')
        self.user = User.objects.get(username='coordinator0')

    def test_no_login(self):
        self.client.logout()
        response = self.client.get(self.url_1, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + self.url_1)

    def test_insufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

    def test_insufficient_permissions_deletion_with_grades(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_3)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.get(self.url_3, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, self.view_cls.as_view().__name__)
        self.assertTemplateUsed(response, self.template)

        self.assertEqual(response.context[self.model_name], self.model_cls.objects.get(pk=self.pk_3))

    def test_deletion(self):
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_3, follow=True)

        self.assertRedirects(response, self.redirect_url)
        self.assertFalse(Test.objects.filter(pk=self.pk_3))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_base(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(6):
            self.client.get(self.url_3)

        with self.assertNumQueries(7):
            self.client.post(self.url_3)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_independent(self):
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(6):
            self.client.get(self.url_3)

        with self.assertNumQueries(7):
            self.client.post(self.url_3)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_dependent(self):
        set_up_large_dependent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(6):
            self.client.get(self.url_3)

        with self.assertNumQueries(7):
            self.client.post(self.url_3)

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries_all(self):
        set_up_large_dependent_data()
        set_up_large_independent_data()
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(6):
            self.client.get(self.url_3)

        with self.assertNumQueries(7):
            self.client.post(self.url_3)


class ModuleManagementRemoveUserTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:user_delete'
        self.pk_1 = Person.objects.get(university_number='s6').pk
        mod_1 = Module.objects.get(name='Module 1').pk
        self.pk_2 = ModuleEdition.objects.get(module=mod_1, block='1A', year=timezone.now().year).pk
        self.pk_3 = Person.objects.get(university_number='s5').pk
        self.pk_4 = Person.objects.get(university_number='s0').pk
        mod_2 = Module.objects.get(name='Module 2').pk
        self.pk_5 = ModuleEdition.objects.get(module=mod_2, block='1B', year=timezone.now().year).pk
        self.url_1 = reverse(self.base_url, kwargs={'spk': self.pk_1, 'mpk': self.pk_2})
        self.url_2 = reverse(self.base_url, kwargs={'spk': self.pk_3, 'mpk': self.pk_5})
        self.url_3 = reverse(self.base_url, kwargs={'spk': self.pk_4, 'mpk': self.pk_2})
        self.user = User.objects.get(username='coordinator0')

    def test_no_login(self):
        self.client.logout()
        response = self.client.get(self.url_1, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + self.url_1)

    def test_insufficient_permissions(self):
        # Login as student
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='student0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_3)
        self.assertEqual(response.status_code, 403)

        # Login as teaching assistant
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_3)
        self.assertEqual(response.status_code, 403)

        # Login as teacher
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='teacher0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_3)
        self.assertEqual(response.status_code, 403)

        # Login as study adviser
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='study_adviser0'))
        response = self.client.get(self.url_1)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.url_3)
        self.assertEqual(response.status_code, 403)

        # Login as wrong coordinator
        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(self.url_2)
        self.assertEqual(response.status_code, 403)

    def test_sufficient_permissions(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        response = self.client.get(self.url_1, follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.url_3, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        """Currently broken, probably related to the response being a JsonResponse"""
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        name = Person.objects.get(pk=self.pk_1).name
        number = Person.objects.get(pk=self.pk_1).university_number
        pk = Person.objects.get(pk=self.pk_1).pk
        code = ModuleEdition.objects.get(pk=self.pk_2).code
        module_name = ModuleEdition.objects.get(pk=self.pk_2).module.name

        response = self.client.get(self.url_1, follow=True)
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content.decode())

        self.assertEqual(response_content['person_name'], name)
        self.assertEqual(response_content['person_number'], number)
        self.assertEqual(response_content['person_pk'], pk)
        self.assertEqual(response_content['module_code'], code)
        self.assertEqual(response_content['module_name'], module_name)
        self.assertTrue(response_content['success'])

        name = Person.objects.get(pk=self.pk_4).name
        number = Person.objects.get(pk=self.pk_4).university_number
        pk = Person.objects.get(pk=self.pk_4).pk
        code = ModuleEdition.objects.get(pk=self.pk_2).code
        module_name = ModuleEdition.objects.get(pk=self.pk_2).module.name

        response = self.client.get(self.url_3)
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, self.template)

        response_content = json.loads(response.content.decode())

        self.assertEqual(response_content['person_name'], name)
        self.assertEqual(response_content['person_number'], number)
        self.assertEqual(response_content['person_pk'], pk)
        self.assertEqual(response_content['module_code'], code)
        self.assertEqual(response_content['module_name'], module_name)
        self.assertFalse(response_content['success'])

    def test_deletion(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        self.assertTrue(Studying.objects.filter(person=self.pk_1, module_edition=self.pk_2))
        self.client.post(self.url_1, follow=True)
        self.assertFalse(Studying.objects.filter(person=self.pk_1, module_edition=self.pk_2))

        self.assertTrue(Studying.objects.filter(person=self.pk_4, module_edition=self.pk_2))
        self.client.post(self.url_3, follow=True)
        self.assertTrue(Studying.objects.filter(person=self.pk_4, module_edition=self.pk_2))

    @skipIf(not _RUN_QUERY_TESTS, 'Only run this test to check the number of queries, e.g. to find n+1 queries.')
    def test_queries(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(11):
            self.client.get(self.url_1)
