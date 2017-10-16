from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from Grades.models import Module, Person, Study, ModuleEdition, ModulePart, Studying, Test, Grade, Teacher, Coordinator
from Seth.settings import LOGIN_URL
from module_management.views import ModuleListView, ModuleDetailView, ModuleEditionDetailView, TestDetailView, ModuleEditionUpdateView, \
    ModulePartUpdateView, ModulePartDetailView, ModulePartDeleteView, TestDeleteView, TestUpdateView, ModuleEditionCreateView, \
    ModuleEditionCreateForm, ModulePartCreateView, ModulePartCreateForm, TestCreateView, TestCreateForm


def set_up_base_data():
    # Define Users
    student_user0 = User(username='student0', password='secure_password')
    student_user1 = User(username='student1', password='secure_password')
    teaching_assistant_user = User(username='teaching_assistant0', password='secure_password')
    teacher_user = User(username='teacher0', password='secure_password')
    study_adviser_user = User(username='study_adviser0', password='secure_password')
    coordinator_user = User(username='coordinator0', password='secure_password')
    student_user0.save()
    student_user1.save()
    teaching_assistant_user.save()
    teacher_user.save()
    study_adviser_user.save()
    coordinator_user.save()

    # Define Persons
    student_person0 = Person(university_number='s0', name='Student 0', user=student_user0)
    teaching_assistant_person = Person(university_number='s1', name='Teaching Assistant 0', user=teaching_assistant_user)
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

    module_part1 = ModulePart(name='module_part1', module_edition=module_ed1)
    module_part1.save()

    module_part2 = ModulePart(name='module_part2', module_edition=module_ed0)
    module_part2.save()

    # Define Studying
    studying = Studying(person=student_person0, study=study, module_edition=module_ed0, role='student')
    studying.save()

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

    # Define Coordinators
    coordinator0 = Coordinator(person=coordinator_person, module_edition=module_ed0, is_assistant=False)
    coordinator0.save()

    coordinator1 = Coordinator(person=coordinator_person, module_edition=module_ed3, is_assistant=False)
    coordinator1.save()


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
        self.assertTemplateUsed(response, 'module_management/module_overview2.html')

        self.assertQuerysetEqual(response.context['module_list'],
                                 get_list_from_queryset(Module.objects.filter(moduleedition__coordinators__user=user).distinct()))
        self.assertQuerysetEqual(response.context['mod_eds'], get_list_from_queryset(ModuleEdition.objects.filter(coordinators__user=user)))

        self.assertContains(response, 'Module 1')
        self.assertContains(response, '{}-{}-{}'.format(timezone.now().year, '001', '1A'))
        self.assertContains(response, '{}-{}-{}'.format(timezone.now().year - 1, '001', '1A'))
        self.assertNotContains(response, '{}-{}-{}'.format(timezone.now().year - 2, '001', '1A'))
        self.assertNotContains(response, 'Module 2')
        self.assertNotContains(response, '{}-{}-{}'.format(timezone.now().year, '002', '1B'))

    def test_queries(self):
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
        pk = Module.objects.get(code='001').pk

        self.client.logout()
        url = reverse('module_management:module_detail', kwargs={'pk': pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        pk_1 = Module.objects.get(code='001').pk
        pk_2 = Module.objects.get(code='002').pk

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
        pk_1 = Module.objects.get(code='001').pk

        self.client.logout()
        self.client.force_login(user=User.objects.get(username='coordinator0'))
        response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk_1}))
        self.assertEqual(response.status_code, 200)

    def test_contents(self):
        user = User.objects.get(username='coordinator0')
        pk = Module.objects.get(code='001').pk

        # Log in as coordinator
        self.client.logout()
        self.client.force_login(user=user)
        response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk}))

        self.assertEqual(response.resolver_match.func.__name__, ModuleDetailView.as_view().__name__)
        self.assertTemplateUsed(response, 'module_management/module_detail.html')

        self.assertEqual(response.context['module'], Module.objects.get(pk=pk))
        self.assertQuerysetEqual(response.context['module_editions'], get_list_from_queryset(ModuleEdition.objects.filter(coordinators__user=user)))

    def test_queries(self):
        user = User.objects.get(username='coordinator0')
        pk_1 = Module.objects.get(name='Module 1').pk
        url_1 = reverse('module_management:module_detail', kwargs={'pk': pk_1})

        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=user)

        with self.assertNumQueries(7):
            self.client.get(url_1, follow=True)


class ModuleManagementModuleEditionDetailTests(TestCase):
    def setUp(self):
        set_up_base_data()

    def test_no_login(self):
        pk = ModuleEdition.objects.get(module='001', block='1A', year=timezone.now().year).pk

        self.client.logout()
        url = reverse('module_management:module_edition_detail', kwargs={'pk': pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, LOGIN_URL + '?next=' + url)

    def test_insufficient_permissions(self):
        pk_1 = ModuleEdition.objects.get(module='001', block='1A', year=timezone.now().year).pk
        pk_2 = ModuleEdition.objects.get(module='001', block='1A', year=timezone.now().year - 2).pk
        pk_3 = ModuleEdition.objects.get(module='002', block='1B', year=timezone.now().year).pk
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
        module_edition = ModuleEdition.objects.get(module='001', block='1A', year=timezone.now().year).pk
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

    def test_queries(self):
        user = User.objects.get(username='coordinator0')
        pk_1 = ModuleEdition.objects.get(module='001', block='1A', year=timezone.now().year).pk
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
        self.pk_1 = self.model_cls.objects.get(module='001', block='1A', year=timezone.now().year).pk
        self.url_1 = reverse(self.base_url, kwargs={'pk': self.pk_1})
        self.user = User.objects.get(username='coordinator0')

    def test_fields_required(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1, {})
        self.assertFormError(response, 'form', 'year', 'This field is required.')
        self.assertFormError(response, 'form', 'block', 'This field is required.')
        self.assertFormError(response, 'form', 'start', 'This field is required.')
        self.assertFormError(response, 'form', 'end', 'This field is required.')

    def test_protected_fields(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        self.client.post(self.url_1,
                         {'year': 2020, 'block': '1A', 'start': '2017-10-11', 'end': '2017-10-11', 'module': Module.objects.get(code='002').pk})
        self.assertEqual('001', ModuleEdition.objects.get(year=2020).module.code)

    def test_invalid_input_year(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1, {'year': 'a', 'block': '1A', 'start': '2017-10-11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'year', 'Enter a whole number.')
        response = self.client.post(self.url_1, {'year': 2017.2, 'block': '1A', 'start': '2017-10-11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'year', 'Enter a whole number.')

    def test_invalid_input_block(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1C', 'start': '2017-10-11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'block', 'Select a valid choice. 1C is not one of the available choices.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1', 'start': '2017-10-11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'block', 'Select a valid choice. 1 is not one of the available choices.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': 1, 'start': '2017-10-11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'block', 'Select a valid choice. 1 is not one of the available choices.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': 'Block 1A', 'start': '2017-10-11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'block', 'Select a valid choice. Block 1A is not one of the available choices.')

    def test_invalid_input_start(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': '2017-13-11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'start', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': '2017-0-11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'start', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': '2017-10-0', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'start', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': '2017-10-32', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'start', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': '2017-02-29', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'start', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': '2017--1-11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'start', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': 'a-10-11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'start', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': '2017 10 11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'start', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': '2017-20-11', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'start', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': '2017-10-11 10:10:10', 'end': '2017-10-11'})
        self.assertFormError(response, 'form', 'start', 'Enter a valid date.')

    def test_invalid_input_end(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'end': '2017-13-11', 'start': '2017-10-11'})
        self.assertFormError(response, 'form', 'end', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'end': '2017-0-11', 'start': '2017-10-11'})
        self.assertFormError(response, 'form', 'end', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'end': '2017-10-0', 'start': '2017-10-11'})
        self.assertFormError(response, 'form', 'end', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'end': '2017-10-32', 'start': '2017-10-11'})
        self.assertFormError(response, 'form', 'end', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'end': '2017-02-29', 'start': '2017-10-11'})
        self.assertFormError(response, 'form', 'end', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'end': '2017--1-11', 'start': '2017-10-11'})
        self.assertFormError(response, 'form', 'end', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'end': 'a-10-11', 'start': '2017-10-11'})
        self.assertFormError(response, 'form', 'end', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'end': '2017 10 11', 'start': '2017-10-11'})
        self.assertFormError(response, 'form', 'end', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'end': '2017-20-11', 'start': '2017-10-11'})
        self.assertFormError(response, 'form', 'end', 'Enter a valid date.')
        response = self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'end': '2017-10-11 10:10:10', 'start': '2017-10-11'})
        self.assertFormError(response, 'form', 'end', 'Enter a valid date.')


class ModuleManagementModuleEditionUpdateTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:module_edition_update'
        self.template = 'module_management/module_edition_update.html'
        self.view_cls = ModuleEditionUpdateView
        self.model_cls = ModuleEdition
        self.model_name = 'moduleedition'
        self.pk_1 = self.model_cls.objects.get(module='001', block='1A', year=timezone.now().year).pk
        self.pk_2 = self.model_cls.objects.get(module='001', block='1A', year=timezone.now().year - 2).pk
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
        self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': '2017-10-11', 'end': '2017-10-11'})
        self.assertFalse(ModuleEdition.objects.filter(year=timezone.now().year, block='1A'))
        self.assertTrue(ModuleEdition.objects.filter(year=2020))

    def test_queries(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(6):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(5):
            self.client.post(self.url_1, {'year': 2020, 'block': '1A', 'start': '2017-10-11', 'end': '2017-10-11'})


# WIP
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
        self.pk_1 = self.super_cls.objects.get(code='001').pk
        self.pk_2 = self.super_cls.objects.get(code='002').pk
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

    def test_queries(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(16):
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

    def test_queries(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(9):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(10):
            self.client.post(self.url_3, {'name': 'module_part2_new', 'teachers': (self.person1, self.person2)})


# WIP
class ModuleManagementModulePartCreateTests(TestCase):
    def setUp(self):
        set_up_base_data()
        self.base_url = 'module_management:module_part_create'
        self.template = 'module_management/module_part_create.html'
        self.view_cls = ModulePartCreateView
        self.model_cls = ModulePart
        self.model_name = 'modulepart'
        self.super_cls = ModuleEdition
        self.form_cls = ModulePartCreateForm
        self.pk_1 = self.super_cls.objects.get(module='001', block='1A', year=timezone.now().year).pk
        self.pk_2 = self.super_cls.objects.get(module='001', block='1A', year=timezone.now().year - 2).pk
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

    def test_queries(self):
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

    def test_queries(self):
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
        self.assertFormError(response, 'form', 'time', 'This field is required.')
        self.assertFormError(response, 'form', 'maximum_grade', 'This field is required.')
        self.assertFormError(response, 'form', 'minimum_grade', 'This field is required.')

    def test_protected_fields(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        self.client.post(self.url_1,
                         {'name': 'newname', 'type': 'E', 'maximum_grade': 10, 'minimum_grade': 1, 'time': '2017-10-11 13:37:00',
                          'module_part': ModulePart.objects.get(name='module_part1').pk})
        self.assertEqual(Test.objects.get(pk=self.pk_1).module_part.pk, ModulePart.objects.get(name='module_part0').pk)

    def test_invalid_input_name(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        s = ''
        for i in range(256):
            s = s + str(i)
        response = self.client.post(self.url_1, {'name': s, 'type': 'E', 'maximum_grade': 10, 'minimum_grade': 1, 'time': '2017-10-11 13:37:00'})
        self.assertFormError(response, 'form', 'name', 'Ensure this value has at most 255 characters (it has 658).')

    def test_invalid_input_type(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'Exam', 'maximum_grade': 10, 'minimum_grade': 1, 'time': '2017-10-11 13:37:00'})
        self.assertFormError(response, 'form', 'type', 'Select a valid choice. Exam is not one of the available choices.')
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'X', 'maximum_grade': 10, 'minimum_grade': 1, 'time': '2017-10-11 13:37:00'})
        self.assertFormError(response, 'form', 'type', 'Select a valid choice. X is not one of the available choices.')
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 0, 'maximum_grade': 10, 'minimum_grade': 1, 'time': '2017-10-11 13:37:00'})
        self.assertFormError(response, 'form', 'type', 'Select a valid choice. 0 is not one of the available choices.')

    def test_invalid_input_time(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'E', 'maximum_grade': 10, 'minimum_grade': 1, 'time': '2017-10-11 25:37:00'})
        self.assertFormError(response, 'form', 'time', 'Enter a valid date/time.')
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'E', 'maximum_grade': 10, 'minimum_grade': 1, 'time': '2017-10-eleven 13:37:00'})
        self.assertFormError(response, 'form', 'time', 'Enter a valid date/time.')
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'E', 'maximum_grade': 10, 'minimum_grade': 1, 'time': '2017-13-11 13:37:00'})
        self.assertFormError(response, 'form', 'time', 'Enter a valid date/time.')

    def test_invalid_input_maximum_grade(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'E', 'maximum_grade': 100000, 'minimum_grade': 1, 'time': '2017-10-11 13:37:00'})
        self.assertFormError(response, 'form', 'maximum_grade', 'Ensure that there are no more than 4 digits in total.')
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'E', 'maximum_grade': 'Ten', 'minimum_grade': 1, 'time': '2017-10-11 13:37:00'})
        self.assertFormError(response, 'form', 'maximum_grade', 'Enter a number.')

    def test_invalid_input_minimum_grade(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'E', 'minimum_grade': 100000, 'maximum_grade': 1, 'time': '2017-10-11 13:37:00'})
        self.assertFormError(response, 'form', 'minimum_grade', 'Ensure that there are no more than 4 digits in total.')
        response = self.client.post(self.url_1,
                                    {'name': 'newname', 'type': 'E', 'minimum_grade': 'Ten', 'maximum_grade': 1, 'time': '2017-10-11 13:37:00'})
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
        self.client.post(self.url_1, {'name': 'test0_new', 'type': 'P', 'time': '2017-10-11 13:37:00', 'maximum_grade': '1', 'minimum_grade': '10'})
        self.assertFalse(Test.objects.filter(name='test0'))
        self.assertTrue(Test.objects.filter(name='test0_new'))
        self.assertEquals('P', Test.objects.get(pk=self.pk_1).type)

    def test_queries(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(5):
            self.client.get(self.url_1, follow=True)

        with self.assertNumQueries(5):
            self.client.post(self.url_1,
                             {'name': 'test0_new', 'type': 'P', 'time': '2017-10-11 13:37:00', 'maximum_grade': '1', 'minimum_grade': '10'})


# WIP
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

    def test_queries(self):
        # Login as coordinator
        self.client.logout()
        self.client.force_login(user=self.user)

        with self.assertNumQueries(6):
            self.client.get(self.url_3)

        with self.assertNumQueries(7):
            self.client.post(self.url_3)
