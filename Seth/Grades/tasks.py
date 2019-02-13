from celery.utils.log import get_task_logger
from django.core.mail import send_mail
# from mailing.mail import send_email
from Grades.models import Person
from Seth.celery import app


logger = get_task_logger(__name__)

@app.task()
def send_grade_email_task(students, subject, message, domain):
    logger.info("Sent grade emails")

    student_emails = [v.email for v in Person.objects.filter(pk__in=students)]

    for email in student_emails:
        send_mail(
            from_email='noreply_seth@{}'.format(domain),
            recipient_list=[email],
            subject=subject,
            message=message,
        )
    return True
