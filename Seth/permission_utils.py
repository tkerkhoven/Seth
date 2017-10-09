from Grades.models import Coordinator, Teacher, Studying, Study
from django.db.models import Q
import datetime


def is_coordinator(person):
    today = now()
    result = Coordinator.objects.filter(person=person, is_assistant=False)
    result = result.filter(Q(person__end__gte=today) | Q(person__end=None))
    return result.count() > 0


def is_coordinator_of_module(person, mid):
    """Untested"""
    today = now()
    result = Coordinator.objects.filter(person=person, module_edition=mid, is_assistant=False)
    result = result.filter(Q(person__end__gte=today) | Q(person__end=None))
    return result.count() > 0


def is_teacher(person):
    today = now()
    result = Teacher.objects.filter(person=person, role='T')
    result = result.filter(Q(person__end__gte=today) | Q(person__end=None))
    return result.count() > 0


def is_teacher_of_part(person, mp):
    """Untested"""
    today = now()
    result = Teacher.objects.filter(person=person, module_part=mp, role='T')
    result = result.filter(Q(person__end__gte=today) | Q(person__end=None))
    return result.count() > 0


def is_teaching_assistant(person):
    today = now()
    result = Teacher.objects.filter(person=person, role='A')
    result = result.filter(Q(person__end__gte=today) | Q(person__end=None))
    return result.count() > 0


def is_teaching_assistant_of_part(person, mpid):
    """Untested"""
    today = now()
    result = Teacher.objects.filter(person=person, role='A', module_part=mpid)
    result = result.filter(Q(person__end__gte=today) | Q(person__end=None))
    return result.count() > 0


def is_student(person):
    today = now()
    result = Studying.objects.filter(person=person)
    result = result.filter(Q(person__end__gte=today) | Q(person__end=None))
    return result.count() > 0


def is_student_of_module(person, mid):
    """Untested"""
    today = now()
    result = Studying.objects.filter(person=person, module_edition=mid)
    # print(result)
    result = result.filter(Q(person__end__gte=today) | Q(person__end=None))
    return result.count() > 0


def is_study_adviser(person):
    today = now()
    result = Study.objects.filter(advisers=person)
    result = result.filter(Q(advisers__end__gte=today) | Q(advisers__end=None))
    return result.count() > 0


def is_study_adviser_of_study(person, study):
    """Untested"""
    today = now()
    result = Study.objects.filter(abbreviation=study.abbreviation)
    result = result.filter(Q(advisers__end__gte=today) | Q(advisers__end=None))
    for study in result:
        if person in study.advisers.all():
            return True
    return False


def is_coordinator_assistant(person):
    result = Coordinator.objects.filter(person=person, is_assistant=True)
    result = result.filter(Q(person__end__gte=now()) | Q(person__end=None))
    return result.count() > 0


def is_coordinator_assistant_of_module(person, mid):
    """Untested"""
    today = now()
    result = Coordinator.objects.filter(person=person, is_assistant=True, module_edition=mid)
    result = result.filter(Q(person__end__gte=today) | Q(person__end=None))
    return result.count() > 0


def is_coordinator_or_assistant(person):
    return is_coordinator(person) or is_coordinator_assistant(person)


def is_coordinator_or_assistant_of_module(person, mid):
    return is_coordinator_of_module(person, mid) or is_coordinator_assistant_of_module(person, mid)


def now():
    return datetime.datetime.now()
