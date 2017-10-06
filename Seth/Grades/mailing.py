from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

from Grades.models import *


def make_mail_grade_released(person, coordinator, grade=None, test=None):
    if not test:
        test = grade.test
    module_edition = test.module_part.module_edition

    email = EmailMultiAlternatives(
        to=person.email,
        subject='[SETH] {} ({}-{}) Grade released: {}'.format(module_edition.module.name, module_edition.year,
                                                              module_edition.block, test.name),
        body=render_to_string('Grades/mailing_grade_released.txt', {
            'person': person,
            'test': test,
            'domain': 'example.com',
            'gradebook_path': reverse('grades:student', kwargs={'pk':person.id}),
            'module_coordinator': module_edition.coordinators.get(user=coordinator)
        })
    )
    email.attach_alternative(render_to_string('Grades/mailing_grade_released.html', {
        'person': person,
        'test': test,
        'domain': 'example.com',
        'gradebook_path': reverse('grades:student'),
            'module_coordinator': module_edition.coordinators.get(user=coordinator)
    }), "text/html")

    return email


def make_mail_grade_retracted(person, grade=None, test=None):
    if not test:
        test = grade.test
    module_edition = test.module_part.module_edition

    email = EmailMultiAlternatives(
        to=person.email,
        subject='[SETH] {} ({}-{}) Grade retracted: {}'.format(module_edition.module.name, module_edition.year,
                                                              module_edition.block, test.name),
        body=render_to_string('Grades/mailing_grade_retracted.txt', {
            'person': person,
            'test': test,
            'domain': 'example.com',
            'gradebook_path': reverse('grades:student'),
            'module_coordinator': module_edition.coordinators[0]
        })
    )
    email.attach_alternative(render_to_string('Grades/mailing_grade_retracted.html', {
        'person': person,
        'test': test,
        'domain': 'example.com',
        'gradebook_path': reverse('grades:student'),
        'module_coordinator': module_edition.coordinators[0]
    }), "text/html")

    return email


