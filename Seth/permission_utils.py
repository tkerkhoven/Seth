from Grades.models import Coordinator, Teacher, Studying, Study, Test, ModulePart
from django.db.models import Q
import datetime


def is_coordinator(person):
    result = Coordinator.objects.filter(person=person, is_assistant=False)
    return result.count() > 0


def is_coordinator_of_module(person, module_edition):
    result = Coordinator.objects.filter(person=person, module_edition=module_edition, is_assistant=False)
    return result.count() > 0


def u_is_coordinator_of_module(user, module_edition):
    result = Coordinator.objects.filter(person__user=user, module_edition=module_edition, is_assistant=False)
    return result.count() > 0


def is_teacher(person):
    result = Teacher.objects.filter(person=person, role='T')
    return result.count() > 0


def is_teacher_of_part(person, module_part):
    result = Teacher.objects.filter(person=person, module_part=module_part, role='T')
    return result.count() > 0


def is_teaching_assistant(person):
    result = Teacher.objects.filter(person=person, role='A')
    return result.count() > 0


def is_teaching_assistant_of_part(person, module_part):
    result = Teacher.objects.filter(person=person, role='A', module_part=module_part)
    return result.count() > 0


def is_student(person):
    result = Studying.objects.filter(person=person)
    return result.count() > 0


def is_student_of_module(person, module_part):
    result = Studying.objects.filter(person=person, module_edition=module_part)
    return result.count() > 0


def is_study_adviser(person):
    result = Study.objects.filter(advisers=person)
    return result.count() > 0


def is_study_adviser_of_study(person, study):
    return Study.objects.filter(advisers=person).filter(
        pk=study.pk).count() > 0


def is_coordinator_assistant(person):
    result = Coordinator.objects.filter(person=person, is_assistant=True)
    return result.count() > 0


def is_coordinator_assistant_of_module(person, module_edition):
    result = Coordinator.objects.filter(person=person, is_assistant=True, module_edition=module_edition)
    return result.count() > 0


def is_coordinator_or_assistant(person):
    return is_coordinator(person) or is_coordinator_assistant(person)


def is_coordinator_or_assistant_of_module(person, module_edition):
    return is_coordinator_of_module(person, module_edition) or is_coordinator_assistant_of_module(person,
                                                                                                  module_edition)


# Test related queries
# untested

def is_coordinator_or_teacher_of_test(person, test):
    """ Tests whether a person is coordinator (assistant) or teacher of a test.
    """
    return Test.objects.filter(
        Q(module_part__teachers=person) |
        Q(module_part__module_edition__coordinator__person=person)
    ).filter(pk=test.pk).count() > 0

# Test related queries
# untested

def is_coordinator_or_teacher_of_module_part(person, module_part):
    """ Tests whether a person is coordinator (assistant) or teacher of a test.
    """
    return ModulePart.objects.filter(
        Q(teachers=person) |
        Q(module_edition__coordinator__person=person)
    ).filter(pk=module_part.pk).count() > 0

