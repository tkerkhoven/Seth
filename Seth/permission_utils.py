from django.db.models import Q

from Grades.models import Coordinator, Teacher, Studying, Study, Test, ModulePart


# Role checks. Only usable in overview pages.

def is_coordinator(person):
    return person and Coordinator.objects.filter(person=person, is_assistant=False).count() > 0


def is_coordinator_assistant(person):
    return person and Coordinator.objects.filter(person=person, is_assistant=True).count() > 0


def is_coordinator_or_assistant(person):
    return person and is_coordinator(person) or is_coordinator_assistant(person)


def is_teacher(person):
    return person and Teacher.objects.filter(person=person, role='T').count() > 0


def is_teaching_assistant(person):
    result = Teacher.objects.filter(person=person, role='A')
    return person and result.count() > 0


# Role checkers for specific modules and module parts

def is_coordinator_of_module(person, module_edition):
    return person and Coordinator.objects.filter(person=person, module_edition=module_edition, is_assistant=False).count() > 0


def u_is_coordinator_of_module(user, module_edition):
    return user and Coordinator.objects.filter(person__user=user, module_edition=module_edition, is_assistant=False).count() > 0


def is_coordinator_assistant_of_module(person, module_edition):
    return person and Coordinator.objects.filter(person=person, is_assistant=True, module_edition=module_edition).count() > 0


def u_is_coordinator_assistant_of_module(user, module_edition):
    return user and Coordinator.objects.filter(person__user=user, is_assistant=True, module_edition=module_edition).count() > 0


def is_coordinator_or_assistant_of_module(person, module_edition):
    return person and is_coordinator_of_module(person, module_edition) or is_coordinator_assistant_of_module(person,
                                                                                                  module_edition)


def u_is_coordinator_or_assistant_of_module(user, module_edition):
    return user and u_is_coordinator_of_module(user, module_edition) or u_is_coordinator_assistant_of_module(user,
                                                                                                  module_edition)


def is_teacher_of_part(person, module_part):
    return person and Teacher.objects.filter(person=person, module_part=module_part, role='T').count() > 0


def u_is_teacher_of_part(user, module_part):
    return user and Teacher.objects.filter(person__user=user, module_part=module_part, role='T').count() > 0


def is_teaching_assistant_of_part(person, module_part):
    return person and Teacher.objects.filter(person=person, role='A', module_part=module_part).count() > 0


def u_is_teaching_assistant_of_part(user, module_part):
    return user and Teacher.objects.filter(person__user=user, role='A', module_part=module_part).count() > 0


def is_student(person):
    result = Studying.objects.filter(person=person)
    return person and result.count() > 0


def is_student_of_module(person, module_part):
    result = Studying.objects.filter(person=person, module_edition=module_part)
    return person and result.count() > 0


def is_study_adviser(person):
    result = Study.objects.filter(advisers=person)
    return person and result.count() > 0


def is_study_adviser_of_study(person, study):
    return person and Study.objects.filter(advisers=person).filter(
        pk=study.pk).count() > 0


# Test related queries
# untested

def is_coordinator_or_teacher_of_test(person, test):
    """ Tests whether a person is coordinator (assistant) or teacher of a test.
    """
    if person is None:
        return False
    return Test.objects.filter(
        Q(module_part__teachers=person) |
        Q(module_part__module_edition__coordinator__person=person)
    ).filter(pk=test.pk).count() > 0


# Test related queries
# untested

def is_coordinator_or_teacher_of_module_part(person, module_part):
    """ Tests whether a person is coordinator (assistant) or teacher of a test.
    """
    if person is None:
        return False
    return ModulePart.objects.filter(
        Q(teachers=person) |
        Q(module_edition__coordinator__person=person)
    ).filter(pk=module_part.pk).count() > 0
