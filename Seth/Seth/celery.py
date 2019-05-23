import os
import sys
from celery.utils.log import get_task_logger
from celery import Celery
from Seth import settings
# from celery.decorators import task
# from Grades.models import Person


OS_PATH = '../../'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Seth.settings')

with open('{}secrets/rabbitmq_user'.format(OS_PATH)) as user:
    with open('{}secrets/rabbitmq_pass'.format(OS_PATH)) as passw:
        broker_url = 'amqp://{user}:{passw}@localhost:5672/{user}'.format(
            user=user.read().strip(),
            passw=passw.read().strip())

app = Celery('Seth', broker=broker_url)


app.autodiscover_tasks('Grades')




