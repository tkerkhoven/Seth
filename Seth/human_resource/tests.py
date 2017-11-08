from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase

# Create your tests here.
from django.urls import reverse

from Grades.models import Person, ModuleEdition, Study, Module
from human_resource.views import known_persons
from module_management.tests import set_up_base_data


class KnownPersonsTest(TestCase):

    def setUp(self):
        set_up_base_data()

    def test_as_student(self):
        student = Person.objects.exclude(
            teacher__module_part__module_edition__in=ModuleEdition.objects.all().values_list('id', flat=True)
        ).filter(
            studying__module_edition__in=ModuleEdition.objects.all().values_list('id', flat=True)
        ).first()

        if not student:
            self.fail("No student that is not a student assistant, aborting")

        self.assertEqual(known_persons(student).count(), 0)

    def test_as_student_assistant(self):
        # Module edition with at least one student assistant
        module_edition = ModuleEdition.objects.filter(modulepart__teacher__role='A').first()
        student_assistant = Person.objects.filter(teacher__module_part__module_edition=module_edition)\
            .exclude(teacher__role='T').first()

        queryset = Person.objects.filter(
            Q(studying__module_edition__modulepart__teacher__person=student_assistant) |
            Q(coordinator__module_edition__modulepart__teacher__person=student_assistant) |
            Q(teacher__module_part__module_edition__modulepart__teacher__person=student_assistant)
        ).distinct()

        self.assertQuerysetEqual(queryset.order_by('university_number'), map(repr, known_persons(student_assistant)))

    def test_as_teacher(self):
        module_edition = ModuleEdition.objects.filter(modulepart__teacher__role='T').first()
        teacher = Person.objects.filter(teacher__module_part__module_edition=module_edition)\
            .exclude(teacher__role='A').first()

        queryset = Person.objects.filter(
            Q(studying__module_edition__modulepart__teacher__person=teacher) |
            Q(coordinator__module_edition__modulepart__teacher__person=teacher) |
            Q(teacher__module_part__module_edition__modulepart__teacher__person=teacher)
        ).distinct()

        self.assertQuerysetEqual(queryset.order_by('university_number'), map(repr, known_persons(teacher)))

    def test_as_module_coordinator(self):

        module_coordinator = Person.objects.filter(
            coordinator__module_edition__in=ModuleEdition.objects.all().values_list('id', flat=True),
            coordinator__is_assistant=False
        ).first()

        queryset = Person.objects.filter(
            Q(studying__module_edition__coordinator__person=module_coordinator) |
            Q(teacher__module_part__module_edition__coordinator__person=module_coordinator) |
            Q(coordinator__module_edition__coordinator__person=module_coordinator)
        ).distinct()

        self.assertQuerysetEqual(queryset.order_by('university_number'), map(repr, known_persons(module_coordinator)))

    def test_as_module_coordinator_assistant(self):
        module_coordinator = Person.objects.filter(
            coordinator__module_edition__in=ModuleEdition.objects.all().values_list('id', flat=True),
            coordinator__is_assistant=True
        ).first()

        queryset = Person.objects.filter(
            Q(studying__module_edition__coordinator__person=module_coordinator) |
            Q(teacher__module_part__module_edition__coordinator__person=module_coordinator) |
            Q(coordinator__module_edition__coordinator__person=module_coordinator)
        ).distinct()

        self.assertQuerysetEqual(queryset.order_by('university_number'), map(repr, known_persons(module_coordinator)))

    def test_as_study_adviser(self):
        study_adviser = Person.objects.filter(
            study__modules__in=Module.objects.all().values_list('pk', flat=True)
        )

        queryset = Person.objects.filter(
            Q(studying__module_edition__module__study__advisers=study_adviser) |
            Q(teacher__module_part__module_edition__module__study__advisers=study_adviser) |
            Q(coordinator__module_edition__module__study__advisers=study_adviser)
        ).distinct()

        self.assertQuerysetEqual(queryset.order_by('university_number'), map(repr, known_persons(study_adviser)))

class PersonDetailViewTest(TestCase):

    def setUp(self):
        set_up_base_data()
        self.view = 'human_resource:person'
        self.module_coordinator = Person.objects.filter(
            moduleedition__in=ModuleEdition.objects.all().values_list('id', flat=True),
            coordinator__is_assistant=False
        ).first()
        self.module_coordinator_assistant = Person.objects.filter(
            moduleedition__in=ModuleEdition.objects.all().values_list('id', flat=True),
            coordinator__is_assistant=True
        ).first()

    def test_permissions(self):
        person = Person.objects.get(university_number='s0')

        # dummy user
        self.client.force_login(User.objects.get(username='dummy_user'))
        response = self.client.get(reverse(self.view, args=[person.pk]))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # student user
        self.client.force_login(User.objects.get(username='student0'))
        response = self.client.get(reverse(self.view, args=[person.pk]))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # teacher of student
        self.client.force_login(
            User.objects.filter(person__teacher__module_part__module_edition__studying__person=person).first()
        )
        response = self.client.get(reverse(self.view, args=[person.pk]))
        self.assertTemplateUsed(response, 'human_resource/person.html')
        self.client.logout()

        # teacher, but not of student
        self.client.force_login(
            User.objects.filter(person__teacher__module_part__module_edition__in=
                                ModuleEdition.objects.all().values_list('pk', flat=True))
                .exclude(person__teacher__module_part__module_edition__studying__person=person).first()
        )
        response = self.client.get(reverse(self.view, args=[person.pk]))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Module coordinator
        self.client.force_login(self.module_coordinator.user)
        response = self.client.get(reverse(self.view, args=[person.pk]))
        self.assertTemplateUsed(response, 'human_resource/person.html')
        self.client.logout()

        # Module coordinator
        self.client.force_login(self.module_coordinator_assistant.user)
        response = self.client.get(reverse(self.view, args=[person.pk]))
        self.assertTemplateUsed(response, 'human_resource/person.html')
        self.client.logout()

    def test_contents(self):
        person = Person.objects.all().first()
        person.email = "ppuk@homtail.com"
        person.save()

        self.client.force_login(self.module_coordinator.user)
        response = self.client.get(reverse(self.view, args=[person.pk]))

        web_page = response.content.decode()

        self.assertTrue(person.name in web_page)
        self.assertTrue(person.university_number in web_page)
        self.assertTrue(person.email in web_page)
        for module in ModuleEdition.objects.filter(studying__person=person):
            self.assertTrue(module.name in web_page)
            self.assertTrue(module.block in web_page)
            self.assertTrue(module.year in web_page)

class PersonUpdateViewTest(TestCase):

    def setUp(self):
        set_up_base_data()
        self.view = 'human_resource:update_person'
        self.module_coordinator = Person.objects.filter(
            moduleedition__in=ModuleEdition.objects.all().values_list('id', flat=True),
            coordinator__is_assistant=False
        ).first()
        self.module_coordinator_assistant = Person.objects.filter(
            moduleedition__in=ModuleEdition.objects.all().values_list('id', flat=True),
            coordinator__is_assistant=True
        ).first()

        self.person = Person.objects.get(university_number='s0')
        self.person.email = "ppuk@homtail.com"
        self.person.save()

    def test_permissions(self):

        # dummy user
        self.client.force_login(User.objects.get(username='dummy_user'))
        response = self.client.get(reverse(self.view, args=[self.person.pk]))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # student user
        self.client.force_login(User.objects.get(username='student0'))
        response = self.client.get(reverse(self.view, args=[self.person.pk]))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # teacher of student
        self.client.force_login(
            User.objects.filter(person__teacher__module_part__module_edition__studying__person=self.person).first()
        )
        response = self.client.get(reverse(self.view, args=[self.person.pk]))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # teacher, but not of student
        self.client.force_login(
            User.objects.filter(person__teacher__module_part__module_edition__in=
                                ModuleEdition.objects.all().values_list('pk', flat=True))
                .exclude(person__teacher__module_part__module_edition__studying__person=self.person).first()
        )
        response = self.client.get(reverse(self.view, args=[self.person.pk]))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Module coordinator
        self.client.force_login(self.module_coordinator.user)
        response = self.client.get(reverse(self.view, args=[self.person.pk]))
        self.assertTemplateUsed(response, 'human_resource/person/update-person.html')
        self.client.logout()

        # Module coordinator
        self.client.force_login(self.module_coordinator_assistant.user)
        response = self.client.get(reverse(self.view, args=[self.person.pk]))
        self.assertTemplateUsed(response, 'human_resource/person/update-person.html')
        self.client.logout()

    def test_contents(self):
        self.client.force_login(self.module_coordinator.user)
        response = self.client.get(reverse(self.view, args=[self.person.pk]))

        web_page = response.content.decode()

        self.assertTrue(self.person.name in web_page)
        self.assertTrue(self.person.university_number in web_page)
        self.assertTrue(self.person.email in web_page)

    def test_form_required_fields(self):
        self.client.force_login(self.module_coordinator.user)
        response = self.client.post(reverse(self.view, args=[self.person.pk]), {})
        self.assertFormError(response, 'form', 'name', 'This field is required.')
        self.assertFormError(response, 'form', 'university_number', 'This field is required.')
        self.assertFormError(response, 'form', 'email', 'This field is required.')

    def test_form_invalid_student_number(self):
        other_person = Person.objects.filter(university_number__startswith='s').exclude(pk=self.person.pk).first()
        self.client.force_login(self.module_coordinator.user)
        response = self.client.post(
            reverse(self.view, args=[self.person.pk]),
            {
                'name': self.person.name,
                'university_number': other_person.university_number,
                'email': self.person.email
             })
        self.assertFormError(response, 'form', 'university_number', 'Person with this University number already '
                                                                    'exists.')