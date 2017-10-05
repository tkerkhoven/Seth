from Grades.models import Coordinator, Teacher, Studying, Study
from django.db.models import Q
import datetime


def is_module_coordinator(user):
    today = now()
    result = Coordinator.objects.filter(person__user=user, is_assistant=False)
    result = result.filter(Q(person__end__lte=today) | Q(person__end=None))
    return result.count() > 0


def is_coordinator_of_module(user, mid):
    """Untested"""
    today = now()
    result = Coordinator.objects.filter(person__user=user, module_edition=mid, is_assistant=False)
    result = result.filter(Q(person__end__lte=today) | Q(person__end=None))
    return result.count() > 0


def is_teacher(user):
    today = now()
    result = Teacher.objects.filter(person__user=user, role='T')
    result = result.filter(Q(person__end__lte=today) | Q(person__end=None))
    return result.count() > 0


def is_teacher_of_course(user, mpid):
    """Untested"""
    today = now()
    result = Teacher.objects.filter(person__user=user, module_part=mpid, role='T')
    result = result.filter(Q(person__end__lte=today) | Q(person__end=None))
    return result.count() > 0


def is_teaching_assistant(user):
    today = now()
    result = Teacher.objects.filter(person__user=user, role='A')
    result = result.filter(Q(person__end__lte=today) | Q(person__end=None))
    return result.count() > 0


def is_teaching_assistant_of_course(user, mpid):
    """Untested"""
    today = now()
    result = Teacher.objects.filter(person__user=user, role='A', module_part=mpid)
    result = result.filter(Q(person__end__lte=today) | Q(person__end=None))
    return result.count() > 0


def is_student(user):
    today = now()
    result = Studying.objects.filter(person__user=user)
    result = result.filter(Q(person__end__lte=today) | Q(person__end=None))
    return result.count() > 0


def is_student_of_module(user, mid):
    """Untested"""
    today = now()
    result = Studying.objects.filter(person__user=user, module_edition=mid)
    result = result.filter(Q(person__end__lte=today) | Q(person__end=None))
    return result.count() > 0


def is_study_adviser(user):
    today = now()
    result = Study.objects.filter(advisers__user=user)
    result = result.filter(Q(advisers__end__lte=today) | Q(advisers__end=None))
    return result.count() > 0


def is_study_adviser_of_study(user, sid):
    """Untested"""
    today = now()
    result = Study.objects.filter(advisers__user=user, abbrevation=sid)
    result = result.filter(Q(person__end__lte=today) | Q(person__end=None))
    return result.count() > 0


def is_module_coordinator_assistant(user):
    result = Coordinator.objects.filter(person__user=user, is_assistant=True)
    result = result.filter(Q(person__end__lte=now()) | Q(person__end=None))
    return result.count() > 0


def is_coordinator_assistant_of_module(user, mid):
    """Untested"""
    today = now()
    result = Coordinator.objects.filter(person__user=user, is_assistant=True, module_edition=mid)
    result = result.filter(Q(person__end__lte=today) | Q(person__end=None))
    return result.count() > 0


def now():
    return datetime.datetime.now()
