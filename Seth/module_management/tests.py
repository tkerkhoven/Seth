# from django.contrib.auth.models import User
# from django.test import TestCase
# from django.urls import reverse
#
# from Grades.models import Module, Person, Study, ModuleEdition, ModulePart, Studying, Test, Grade, Teacher, Coordinator
# from Seth.settings import LOGIN_URL
# from module_management.views import IndexView, ModuleView, ModuleEdView
#
#
# class ModuleManagementIndexTests(TestCase):
#     def setUp(self):
#         # Define Users
#         student_user = User(username='student0', password='secure_password')
#         teaching_assistant_user = User(username='teaching_assistant0', password='secure_password')
#         teacher_user = User(username='teacher0', password='secure_password')
#         study_adviser_user = User(username='study_adviser0', password='secure_password')
#         coordinator_user = User(username='coordinator0', password='secure_password')
#         student_user.save()
#         teaching_assistant_user.save()
#         teacher_user.save()
#         study_adviser_user.save()
#         coordinator_user.save()
#
#         # Define Persons
#         student_person = Person(id_prefix='s', name='Student 0', person_id=0, user=student_user)
#         teaching_assistant_person = Person(id_prefix='s', name='Teaching Assistant 0', person_id=1,
#                                            user=teaching_assistant_user)
#         teacher_person = Person(id_prefix='m', name='Teacher 0', person_id=2, user=teacher_user)
#         study_adviser_person = Person(id_prefix='m', name='Study Adviser 0', person_id=3,
#                                       user=study_adviser_user)
#         coordinator_person = Person(id_prefix='m', name='Coordinator 0', person_id=4, user=coordinator_user)
#         student_person.save()
#         teaching_assistant_person.save()
#         teacher_person.save()
#         study_adviser_person.save()
#         coordinator_person.save()
#
#         # Define Modules
#         module0 = Module(module_code='001', name='Module 1')
#         module0.save()
#
#         module1 = Module(module_code='002', name='Module 2')
#         module1.save()
#
#         # Define Study
#         study = Study(short_name='STU', full_name='Study')
#         study.save()
#         study.advisers.add(study_adviser_person)
#         study.modules.add(module0)
#
#         # Define Courses
#         course0 = ModulePart(code='0', code_extension='0', name='course0')
#         course0.save()
#
#         # Define Module Editions
#         module_ed0 = ModuleEdition(module=module0, module_code_extension='0')
#         module_ed0.save()
#         module_ed0.courses.add(course0)
#
#         module_ed1 = ModuleEdition(module=module0, module_code_extension='1')
#         module_ed1.save()
#
#         module_ed2 = ModuleEdition(module=module1, module_code_extension='0')
#         module_ed2.save()
#
#         # Define Studying
#         studying = Studying(student_id=student_person, study=study, module_id=module_ed0, role='student')
#         studying.save()
#
#         # Define Tests
#         test0 = Test(course_id=course0, name='test0', _type='E')
#         test0.save()
#
#         # Define Grades
#         grade0 = Grade(test_id=test0, teacher_id=teacher_person, student_id=student_person, description='grade0',
#                        grade=6)
#         grade0.save()
#
#         # Define Teachers
#         teacher0 = Teacher(course=course0, person=teacher_person, role='T')
#         teaching_assistant0 = Teacher(course=course0, person=teaching_assistant_person, role='A')
#         teacher0.save()
#         teaching_assistant0.save()
#
#         # Define Coordinators
#         coordinator0 = Coordinator(person=coordinator_person, module=module_ed0, mc_assistant=False)
#         coordinator0.save()
#
#     def test_no_login(self):
#         self.client.logout()
#         url = reverse('module_management:module_overview')
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, LOGIN_URL + '?next=' + url)
#
#     def test_insufficient_permissions(self):
#         # Login as student
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='student0'))
#         response = self.client.get(reverse('module_management:module_overview'), follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teaching assistant
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
#         response = self.client.get(reverse('module_management:module_overview'), follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teacher
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teacher0'))
#         response = self.client.get(reverse('module_management:module_overview'), follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as study adviser
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='study_adviser0'))
#         response = self.client.get(reverse('module_management:module_overview'), follow=True)
#         self.assertEqual(response.status_code, 403)
#
#     def test_contents(self):
#         user = User.objects.get(username='coordinator0')
#
#         # Log in as coordinator
#         self.client.logout()
#         self.client.force_login(user=user)
#         response = self.client.get(reverse('module_management:module_overview'), follow=True)
#
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.resolver_match.func.__name__, IndexView.as_view().__name__)
#         self.assertTemplateUsed(response, 'module_management/index.html')
#
#         self.assertContains(response, 'Module 1')
#         self.assertContains(response, '0010')
#         self.assertNotContains(response, '0011')
#         self.assertNotContains(response, 'Module 2')
#         self.assertNotContains(response, '0020')
#
#
# class ModuleManagementModuleDetailTests(TestCase):
#     def setUp(self):
#         # Define Users
#         student_user = User(username='student0', password='secure_password')
#         teaching_assistant_user = User(username='teaching_assistant0', password='secure_password')
#         teacher_user = User(username='teacher0', password='secure_password')
#         study_adviser_user = User(username='study_adviser0', password='secure_password')
#         coordinator_user = User(username='coordinator0', password='secure_password')
#         student_user.save()
#         teaching_assistant_user.save()
#         teacher_user.save()
#         study_adviser_user.save()
#         coordinator_user.save()
#
#         # Define Persons
#         student_person = Person(id_prefix='s', name='Student 0', person_id=0, user=student_user)
#         teaching_assistant_person = Person(id_prefix='s', name='Teaching Assistant 0', person_id=1,
#                                            user=teaching_assistant_user)
#         teacher_person = Person(id_prefix='m', name='Teacher 0', person_id=2, user=teacher_user)
#         study_adviser_person = Person(id_prefix='m', name='Study Adviser 0', person_id=3,
#                                       user=study_adviser_user)
#         coordinator_person = Person(id_prefix='m', name='Coordinator 0', person_id=4, user=coordinator_user)
#         student_person.save()
#         teaching_assistant_person.save()
#         teacher_person.save()
#         study_adviser_person.save()
#         coordinator_person.save()
#
#         # Define Modules
#         module0 = Module(module_code='001', name='Module 1')
#         module0.save()
#
#         module1 = Module(module_code='002', name='Module 2')
#         module1.save()
#
#         # Define Study
#         study = Study(short_name='STU', full_name='Study')
#         study.save()
#         study.advisers.add(study_adviser_person)
#         study.modules.add(module0)
#
#         # Define Courses
#         course0 = ModulePart(code='0', code_extension='0', name='course0')
#         course0.save()
#
#         # Define Module Editions
#         module_ed0 = ModuleEdition(module=module0, module_code_extension='0')
#         module_ed0.save()
#         module_ed0.courses.add(course0)
#
#         module_ed1 = ModuleEdition(module=module0, module_code_extension='1')
#         module_ed1.save()
#
#         module_ed2 = ModuleEdition(module=module1, module_code_extension='0')
#         module_ed2.save()
#
#         # Define Studying
#         studying = Studying(student_id=student_person, study=study, module_id=module_ed0, role='student')
#         studying.save()
#
#         # Define Tests
#         test0 = Test(course_id=course0, name='test0', _type='E')
#         test0.save()
#
#         # Define Grades
#         grade0 = Grade(test_id=test0, teacher_id=teacher_person, student_id=student_person, description='grade0',
#                        grade=6)
#         grade0.save()
#
#         # Define Teachers
#         teacher0 = Teacher(course=course0, person=teacher_person, role='T')
#         teaching_assistant0 = Teacher(course=course0, person=teaching_assistant_person, role='A')
#         teacher0.save()
#         teaching_assistant0.save()
#
#         # Define Coordinators
#         coordinator0 = Coordinator(person=coordinator_person, module=module_ed0, mc_assistant=False)
#         coordinator0.save()
#
#     def test_no_login(self):
#         pk = Module.objects.get(module_code='001').pk
#
#         self.client.logout()
#         url = reverse('module_management:module_detail', kwargs={'pk': pk})
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, LOGIN_URL + '?next=' + url)
#
#     def test_insufficient_permissions(self):
#         pk_1 = Module.objects.get(module_code='001').pk
#         pk_2 = Module.objects.get(module_code='002').pk
#
#         # Login as student
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='student0'))
#         response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk_1}), follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teaching assistant
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
#         response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk_1}), follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teacher
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teacher0'))
#         response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk_1}), follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as study adviser
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='study_adviser0'))
#         response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk_1}), follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as wrong coordinator
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='coordinator0'))
#         response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk_2}), follow=True)
#         self.assertEqual(response.status_code, 403)
#
#     def test_contents(self):
#         user = User.objects.get(username='coordinator0')
#         pk = Module.objects.get(module_code='001').pk
#
#         # Log in as coordinator
#         self.client.logout()
#         self.client.force_login(user=user)
#         response = self.client.get(reverse('module_management:module_detail', kwargs={'pk': pk}), follow=True)
#
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.resolver_match.func.__name__, ModuleView.as_view().__name__)
#         self.assertTemplateUsed(response, 'module_management/module_detail.html')
#
#         self.assertEqual(response.context['module'], Module.objects.get(pk=pk))
#         self.assertContains(response, 'Module 1')
#         self.assertContains(response, '0010')
#         self.assertNotContains(response, '0011')
#         self.assertNotContains(response, '0020')
#
#
# class ModuleManagementModuleEdDetailTests(TestCase):
#     def setUp(self):
#         # Define Users
#         student_user = User(username='student0', password='secure_password')
#         teaching_assistant_user = User(username='teaching_assistant0', password='secure_password')
#         teacher_user = User(username='teacher0', password='secure_password')
#         study_adviser_user = User(username='study_adviser0', password='secure_password')
#         coordinator_user = User(username='coordinator0', password='secure_password')
#         student_user.save()
#         teaching_assistant_user.save()
#         teacher_user.save()
#         study_adviser_user.save()
#         coordinator_user.save()
#
#         # Define Persons
#         student_person = Person(id_prefix='s', name='Student 0', person_id=0, user=student_user)
#         teaching_assistant_person = Person(id_prefix='s', name='Teaching Assistant 0', person_id=1,
#                                            user=teaching_assistant_user)
#         teacher_person = Person(id_prefix='m', name='Teacher 0', person_id=2, user=teacher_user)
#         study_adviser_person = Person(id_prefix='m', name='Study Adviser 0', person_id=3,
#                                       user=study_adviser_user)
#         coordinator_person = Person(id_prefix='m', name='Coordinator 0', person_id=4, user=coordinator_user)
#         student_person.save()
#         teaching_assistant_person.save()
#         teacher_person.save()
#         study_adviser_person.save()
#         coordinator_person.save()
#
#         # Define Modules
#         module0 = Module(module_code='001', name='Module 1')
#         module0.save()
#
#         module1 = Module(module_code='002', name='Module 2')
#         module1.save()
#
#         # Define Study
#         study = Study(short_name='STU', full_name='Study')
#         study.save()
#         study.advisers.add(study_adviser_person)
#         study.modules.add(module0)
#
#         # Define Courses
#         course0 = ModulePart(code='0', code_extension='0', name='course0')
#         course0.save()
#
#         # Define Module Editions
#         module_ed0 = ModuleEdition(module=module0, module_code_extension='0')
#         module_ed0.save()
#         module_ed0.courses.add(course0)
#
#         module_ed1 = ModuleEdition(module=module0, module_code_extension='1')
#         module_ed1.save()
#
#         module_ed2 = ModuleEdition(module=module1, module_code_extension='0')
#         module_ed2.save()
#
#         # Define Studying
#         studying = Studying(student_id=student_person, study=study, module_id=module_ed0, role='student')
#         studying.save()
#
#         # Define Tests
#         test0 = Test(course_id=course0, name='test0', _type='E')
#         test0.save()
#
#         # Define Grades
#         grade0 = Grade(test_id=test0, teacher_id=teacher_person, student_id=student_person, description='grade0',
#                        grade=6)
#         grade0.save()
#
#         # Define Teachers
#         teacher0 = Teacher(course=course0, person=teacher_person, role='T')
#         teaching_assistant0 = Teacher(course=course0, person=teaching_assistant_person, role='A')
#         teacher0.save()
#         teaching_assistant0.save()
#
#         # Define Coordinators
#         coordinator0 = Coordinator(person=coordinator_person, module=module_ed0, mc_assistant=False)
#         coordinator0.save()
#
#     def test_no_login(self):
#         pk = ModuleEdition.objects.get(module='001', module_code_extension='0').pk
#
#         self.client.logout()
#         url = reverse('module_management:module_ed_detail', kwargs={'pk': pk})
#         response = self.client.get(url, follow=True)
#         self.assertRedirects(response, LOGIN_URL + '?next=' + url)
#
#     def test_insufficient_permissions(self):
#         pk_1 = ModuleEdition.objects.get(module='001', module_code_extension='0').pk
#         pk_2 = ModuleEdition.objects.get(module='001', module_code_extension='1').pk
#         pk_3 = ModuleEdition.objects.get(module='002', module_code_extension='0').pk
#         url_1 = reverse('module_management:module_ed_detail', kwargs={'pk': pk_1})
#         url_2 = reverse('module_management:module_ed_detail', kwargs={'pk': pk_2})
#         url_3 = reverse('module_management:module_ed_detail', kwargs={'pk': pk_3})
#
#         # Login as student
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='student0'))
#         response = self.client.get(url_1, follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teaching assistant
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teaching_assistant0'))
#         response = self.client.get(url_1, follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as teacher
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='teacher0'))
#         response = self.client.get(url_1, follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as study adviser
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='study_adviser0'))
#         response = self.client.get(url_1, follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         # Login as wrong coordinator
#         self.client.logout()
#         self.client.force_login(user=User.objects.get(username='coordinator0'))
#         response = self.client.get(url_2, follow=True)
#         self.assertEqual(response.status_code, 403)
#
#         response = self.client.get(url_3, follow=True)
#         self.assertEqual(response.status_code, 403)
#
#     def test_contents(self):
#         user = User.objects.get(username='coordinator0')
#         mod_ed = ModuleEdition.objects.get(module='001', module_code_extension='0').pk
#         url = reverse('module_management:module_ed_detail', kwargs={'pk': mod_ed})
#
#         # Log in as coordinator
#         self.client.logout()
#         self.client.force_login(user=user)
#         response = self.client.get(url, follow=True)
#
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.resolver_match.func.__name__, ModuleEdView.as_view().__name__)
#         self.assertTemplateUsed(response, 'module_management/module_ed_detail.html')
#
#         self.assertEqual(response.context['module_ed'], ModuleEdition.objects.get(pk=mod_ed))
#
