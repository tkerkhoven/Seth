from Grades.models import Coordinator, Teacher, Studying, Study
from django.db.models import Q
import datetime


def is_module_coordinator(user):
    result = Coordinator.objects.filter(person__user=user, is_assistant=False).count() > 0
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def is_coordinator_of_module(user, mid):
    result = Coordinator.objects.filter(person__user=user, module_edition=mid, is_assistant=False).count() > 0
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def is_teacher(user):
    result = Teacher.objects.filter(person__user=user, roles='T').count > 0
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def is_teacher_of_course(user, mpid):
    result = Teacher.objects.filter(person__user=user, module_part=mpid, roles='T').count() > 0
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def is_teaching_assistant(user):
    result = Teacher.objects.filter(person__user=user, roles='A').count() > 0
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def is_teaching_assistant_of_course(user, mpid):
    result = Teacher.objects.filter(person__user=user, roles='A', module_part=mpid).count() > 0
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def is_student(user):
    result = Studying.objects.filter(person__user=user).count() > 0
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def is_student_of_module(user, mid):
    result = Studying.objects.filter(person__user=user, module_edition=mid).count() > 0
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def is_study_adviser(user):
    result = Study.objects.filter(advisers__user=user).count() > 0
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def is_study_adviser_of_study(user, sid):
    result = Study.objects.filter(advisers__user=user, abbrevation=sid)
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def is_module_coordinator_assistant(user):
    result = Coordinator.objects.filter(person__user=user, is_assistant=True).count() > 0
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def is_coordinator_assistant_of_module(user, mid):
    result = Coordinator.objects.filter(person__user=user, is_assistant=True, module_edition=mid).count() > 0
    result = result.filter(Q(person__end__lte=now() | Q(person__end=None)))
    return result


def now():
    return datetime.datetime.now()
