from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from Grades.models import Module, Person, Study, ModuleEdition, ModulePart, Studying, Test, Grade, Teacher, Coordinator
from Seth.settings import LOGIN_URL
from module_management.views import ModuleListView, ModuleDetailView, ModuleEditionDetailView


# def set_up_base_data():
#     # Define Users
#     student_user0 = User(username='student0', password='secure_password')
#     student_user1 = User(username='student1', password='secure_password')
#     teaching_assistant_user = User(username='teaching_assistant0', password='secure_password')
#     teacher_user = User(username='teacher0', password='secure_password')
#     study_adviser_user = User(username='study_adviser0', password='secure_password')
#     coordinator_user = User(username='coordinator0', password='secure_password')
#     student_user0.save()
#     student_user1.save()
#     teaching_assistant_user.save()
#     teacher_user.save()
#     study_adviser_user.save()
#     coordinator_user.save()
#
#     # Define Persons
#     student_person0 = Person(university_number='s0', name='Student 0', user=student_user0)
#     teaching_assistant_person = Person(university_number='s1', name='Teaching Assistant 0', user=teaching_assistant_user)
#     teacher_person = Person(university_number='m2', name='Teacher 0', user=teacher_user)
#     study_adviser_person = Person(university_number='m3', name='Study Adviser 0', user=study_adviser_user)
#     coordinator_person = Person(university_number='m4', name='Coordinator 0', user=coordinator_user)
#     student_person1 = Person(university_number='s5', name='Student 1', user=student_user1)
#     student_person0.save()
#     teaching_assistant_person.save()
#     teacher_person.save()
#     study_adviser_person.save()
#     coordinator_person.save()
#     student_person1.save()
#
#     # Define Modules
#     module0 = Module(code='001', name='Module 1')
#     module0.save()
#
#     module1 = Module(code='002', name='Module 2')
#     module1.save()
#
#     # Define Study
#     study = Study(abbreviation='STU', name='Study')
#     study.save()
#     study.advisers.add(study_adviser_person)
#     study.modules.add(module0)
#
#     # Define Module Editions
#     module_ed0 = ModuleEdition(module=module0, block='1A', year=timezone.now().year)
#     module_ed0.save()
#
#     module_ed1 = ModuleEdition(module=module0, block='1A', year=timezone.now().year - 2)
#     module_ed1.save()
#
#     module_ed2 = ModuleEdition(module=module1, block='1B', year=timezone.now().year)
#     module_ed2.save()
#
#     module_ed3 = ModuleEdition(module=module0, block='1A', year=timezone.now().year - 1)
#     module_ed3.save()
#
#     # Define Module Parts
#     module_part0 = ModulePart(name='module_part0', module_edition=module_ed0)
#     module_part0.save()
#
#     # Define Studying
#     studying = Studying(person=student_person0, study=study, module_edition=module_ed0, role='student')
#     studying.save()
#
#     # Define Tests
#     test0 = Test(module_part=module_part0, name='test0', type='E')
#     test0.save()
#
#     # Define Grades
#     grade0 = Grade(test=test0, teacher=teacher_person, student=student_person0, description='grade0', grade=6)
#     grade1 = Grade(test=test0, teacher=teacher_person, student=student_person1, description='grade0', grade=9)
#     grade0.save()
#     grade1.save()
#
#     # Define Teachers
#     teacher0 = Teacher(module_part=module_part0, person=teacher_person, role='T')
#     teaching_assistant0 = Teacher(module_part=module_part0, person=teaching_assistant_person, role='A')
#     teacher0.save()
#     teaching_assistant0.save()
#
#     # Define Coordinators
#     coordinator0 = Coordinator(person=coordinator_person, module_edition=module_ed0, is_assistant=False)
#     coordinator0.save()
#
#     coordinator1 = Coordinator(person=coordinator_person, module_edition=module_ed3, is_assistant=False)
#     coordinator1.save()


# class ModuleManagementModuleListTests(TestCase):
#     def setUp(self):
#         set_up_base_data()
#
#     def test_no_login(self):
#         self.client.logout()
#         url = reverse('module_management:module_overview')
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, LOGIN_URL + '?next=' + url)
#
#     def test_insufficient_permissions(self):
#         url = reverse('module_management:module_overview')
#
#         # Login as student
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='student0'))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teaching assistant
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teacher
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teacher0'))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as study adviser
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='study_adviser0'))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 403)
#
#     def test_sufficient_permissions(self):
#         # Log in as coordinator
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='coordinator0'))
#         response = self.client.get(reverse('module_management:module_overview'))
#         self.assertEqual(response.status_code, 200)
#
#     def test_contents(self):
#         user = User.objects.get(username='coordinator0')
#
#         # Log in as coordinator
#         self.client.logout()
#         self.client.force_login(user=user)
#         response = self.client.get(reverse('module_management:module_overview'))
#
#         self.assertEqual(response.resolver_match.func.__name__, ModuleListView.as_view().__name__)
#         self.assertTemplateUsed(response, 'module_management/module_overview.html')
#
#         self.assertEqual(response.context['module_list'], Module.objects.filter(moduleedition__coordinators__user=user).distinct())
#         self.assertEqual(response.context['mod_eds'], ModuleEdition.objects.filter(coordinators__user=user))
#
#         self.assertContains(response, 'Module 1')
#         self.assertContains(response, '{}-{}-{}'.format(timezone.now().year, 'Module 1', '1A'))
#         self.assertContains(response, '{}-{}-{}'.format(timezone.now().year - 1, 'Module 1', '1A'))
#         self.assertNotContains(response, '{}-{}-{}'.format(timezone.now().year - 2, 'Module 1', '1A'))
#         self.assertNotContains(response, 'Module 2')
#         self.assertNotContains(response, '{}-{}-{}'.format(timezone.now().year, 'Module 2', '1B'))


# class ModuleManagementModuleDetailTests(TestCase):
#     def setUp(self):
#         set_up_base_data()
#
#     def test_no_login(self):
#         pk = Module.objects.get(code='001').pk
#
#         self.client.logout()
#         url = reverse('module_management:module_detail', kwargs={'pk': pk})
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, LOGIN_URL + '?next=' + url)
#
#     def test_insufficient_permissions(self):
#         pk_1 = Module.objects.get(code='001').pk
#         pk_2 = Module.objects.get(code='002').pk
#
#         url_1 = reverse('module_management:module_detail', kwargs={'pk': pk_1})
#         url_2 = reverse('module_management:module_detail', kwargs={'pk': pk_2})
#
#         # Login as student
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='student0'))
#         response = self.client.get(url_1)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teaching assistant
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
#         response = self.client.get(url_1)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teacher
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teacher0'))
#         response = self.client.get(url_1)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as study adviser
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='study_adviser0'))
#         response = self.client.get(url_1)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as wrong coordinator
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='coordinator0'))
#         response = self.client.get(url_2)
#         self.assertEqual(response.status_code, 403)
#
#     def test_sufficient_permissions(self):
#         pk_1 = Module.objects.get(code='001').pk
#
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='coordinator0'))
#         response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk_1}))
#         self.assertEqual(response.status_code, 200)
#
#     def test_contents(self):
#         user = User.objects.get(username='coordinator0')
#         pk = Module.objects.get(code='001').pk
#
#         # Log in as coordinator
#         self.client.logout()
#         self.client.force_login(user=user)
#         response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk}))
#
#         self.assertEqual(response.resolver_match.func.__name__, ModuleDetailView.as_view().__name__)
#         self.assertTemplateUsed(response, 'module_management/module_detail.html')
#
#         self.assertEqual(response.context['module'], Module.objects.get(pk=pk))
#         self.assertEqual(response.context['module_editions'], ModuleEdition.objects.filter(coordinators__user=user))


# class ModuleManagementModuleEditionDetailTests(TestCase):
#     def setUp(self):
#         set_up_base_data()
#
#     def test_no_login(self):
#         pk = ModuleEdition.objects.get(module='001', block='1A', year=timezone.now().year).pk
#
#         self.client.logout()
#         url = reverse('module_management:module_edition_detail', kwargs={'pk': pk})
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, LOGIN_URL + '?next=' + url)
#
#     def test_insufficient_permissions(self):
#         pk_1 = ModuleEdition.objects.get(module='001', block='1A', year=timezone.now().year).pk
#         pk_2 = ModuleEdition.objects.get(module='001', block='1A', year=timezone.now().year - 2).pk
#         pk_3 = ModuleEdition.objects.get(module='002', block='1B', year=timezone.now().year).pk
#         url_1 = reverse('module_management:module_edition_detail', kwargs={'pk': pk_1})
#         url_2 = reverse('module_management:module_edition_detail', kwargs={'pk': pk_2})
#         url_3 = reverse('module_management:module_edition_detail', kwargs={'pk': pk_3})
#
#         # Login as student
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='student0'))
#         response = self.client.get(url_1)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teaching assistant
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
#         response = self.client.get(url_1)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teacher
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teacher0'))
#         response = self.client.get(url_1)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as study adviser
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='study_adviser0'))
#         response = self.client.get(url_1)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as wrong coordinator
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='coordinator0'))
#         response = self.client.get(url_2)
#         self.assertEqual(response.status_code, 403)
#
#         response = self.client.get(url_3)
#         self.assertEqual(response.status_code, 403)
#
#     def test_contents(self):
#         user = User.objects.get(username='coordinator0')
#         module_edition = ModuleEdition.objects.get(module='001', block='1A', year=timezone.now().year).pk
#         url = reverse('module_management:module_ed_detail', kwargs={'pk': module_edition})
#
#         # Log in as coordinator
#         self.client.logout()
#         self.client.force_login(user=user)
#         response = self.client.get(url, follow=True)
#
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.resolver_match.func.__name__, ModuleEditionDetailView.as_view().__name__)
#         self.assertTemplateUsed(response, 'module_management/module_edition_detail.html')
#
#         self.assertEqual(response.context['moduleedition'], ModuleEdition.objects.get(pk=module_edition))
#         self.assertEqual(response.context['studying'], Studying.objects.filter(module_edition=module_edition))
#         self.assertEqual(response.context['module_parts'], ModulePart.objects.filter(module_edition=module_edition))
#         self.assertEqual(response.context['coordinators'], Coordinator.objects.filter(module_edition=module_edition))
