
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from Grades.models import *
from Grades.tasks import send_grade_email_task


DOMAIN = 'farm11.ewi.utwente.nl'

def mail_module_edition_participants(module_edition, subject, body):
    """Sends an email to all students in a module individually. Returns a list of Persons for which the mailing failed.

    :param module_edition: Module edition to mail to.
    :param subject: Subject line of the email.
    :param body: Body of email.
    :return: list of Persons for which emailing failed.
    """
    students = Person.objects.filter(studying__module_edition=module_edition)

    failed_mails = []

    # Send mails asynchronously
    send_grade_email_task.delay([student.pk for student in students], subject=subject, message=body, domain=DOMAIN)
    return failed_mails


def make_mail_grade_released(person, coordinator, grade=None, test=None):
    """ Generates an EmailMessage that notifies the Person of his grade being released.

    Accepts a Person object, along with either a Grade or a Test. Generates an email with both plaintext and HTML
    content.

    :param person: Recipient, student of the released grade.
    :param grade: Grade object that the student received. Can be empty if test is filled in instead.
    :param test: Test object that the grade was released for. Can be empty if grade is filled in instead.
    :return: The notification mail as an EmailMultiAlternatives object.
    """
    if not test:
        test = grade.test
    module_edition = test.module_part.module_edition

    email = mail.EmailMultiAlternatives(
        from_email='noreply_seth@{}'.format(DOMAIN),
        to=(person.email,),
        subject='[SETH] {} ({}-{}) Grade released: {}'.format(module_edition.module.name, module_edition.year,
                                                              module_edition.block, test.name),
        body=render_to_string('Grades/mailing_grade_released.txt', {
            'person': person,
            'test': test,
            'domain': 'farm11.ewi.utwente.nl',
            'gradebook_path': reverse('grades:student', kwargs={'pk':person.id}),
            'module_coordinator': module_edition.coordinators.get(user=coordinator)
        })
    )
    email.attach_alternative(render_to_string('Grades/mailing_grade_released.html', {
        'person': person,
        'test': test,
        'domain': 'example.com',
        'gradebook_path': reverse('grades:student', kwargs={'pk':person.id}),
        'module_coordinator': module_edition.coordinators.get(user=coordinator)
    }), "text/html")

    return email

def make_mail_grades_released(person, coordinator, module_edition, grades=None, tests=None):
    """ Generates an EmailMessage that notifies the Person of his grade being released.

    Accepts a Person object, along with either a Grade or a Test. Generates an email with both plaintext and HTML
    content.

    :param person: Recipient, student of the released grade.
    :param grade: Grade object that the student received. Can be empty if test is filled in instead.
    :param test: Test object that the grade was released for. Can be empty if grade is filled in instead.
    :return: The notification mail as an EmailMultiAlternatives object.
    """
    if not tests:
        tests = [grade.test for grade in grades]

    tests_by_module_part = {}

    for test in tests:
        if not tests_by_module_part[test.module_part]:
            tests_by_module_part[test.module_part] = [test]
        else:
            tests_by_module_part[test.module_part] += (test)

    email = mail.EmailMultiAlternatives(
        from_email='noreply_seth@{}'.format(DOMAIN),
        to=(person.email,),
        subject='[SETH] {} ({}-{}) Grades released.'.format(module_edition.module.name, module_edition.year,
                                                              module_edition.block),
        body=render_to_string('Grades/mailing_grades_released.jinja', {
            'person': person,
            'tests': tests_by_module_part,
            'domain': 'farm11.ewi.utwente.nl',
            'gradebook_path': reverse('grades:student', kwargs={'pk':person.id}),
            'module_coordinator': module_edition.coordinators.get(user=coordinator)
        })
    )
    email.attach_alternative(render_to_string('Grades/mailing_grades_released_html.jinja', {
        'person': person,
        'tests': tests_by_module_part,
        'domain': 'example.com',
        'gradebook_path': reverse('grades:student', kwargs={'pk':person.id}),
        'module_coordinator': module_edition.coordinators.get(user=coordinator)
    }), "text/html")

    return email

def make_mail_grade_retracted(person, coordinator, grade=None, test=None):
    """ Generates an EmailMessage that notifies the Person of his grade being retracted.

    Accepts a Person object, along with either a Grade or a Test. Generates an email with both plaintext and HTML
    content.

    :param person: Recipient, student of the released grade.
    :param grade: Grade object that the student received. Can be empty if test is filled in instead.
    :param test: Test object that the grade was released for. Can be empty if grade is filled in instead.
    :return: The notification mail as an EmailMultiAlternatives object.
    """
    if not test:
        test = grade.test
    module_edition = test.module_part.module_edition

    email = EmailMultiAlternatives(
        from_email='noreply_seth@{}'.format(DOMAIN),
        to=(person.email,),
        subject='[SETH] {} ({}-{}) Grade retracted: {}'.format(module_edition.module.name, module_edition.year,
                                                              module_edition.block, test.name),
        body=render_to_string('Grades/mailing_grade_retracted.txt', {
            'person': person,
            'test': test,
            'domain': 'example.com',
            'gradebook_path': reverse('grades:student', kwargs={'pk':person.id}),
            'module_coordinator': module_edition.coordinators.get(user=coordinator)
        })
    )
    email.attach_alternative(render_to_string('Grades/mailing_grade_retracted.html', {
        'person': person,
        'test': test,
        'domain': 'example.com',
        'gradebook_path': reverse('grades:student', kwargs={'pk':person.id}),
        'module_coordinator': module_edition.coordinators.get(user=coordinator)
    }), "text/html")

    return email


