from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.utils import timezone

from Grades.models import ModuleEdition, Person, Coordinator, Studying, Grade, ModulePart

from django.contrib.auth.decorators import login_required
import permission_utils as pu
from django.core.exceptions import PermissionDenied


@login_required
def home(request):
    """
    Checks the type of logged in user and directs to an appropriate dashboard with relevant information.

    :param request: Django request for authentication
    :return: Redirect to appropriate dashboard (based on type of user)
    """
    person = Person.objects.get(user=request.user)
    if pu.is_coordinator_or_assistant(person):
        context = {
            'modules': ModuleEdition.objects.filter(coordinator__person=person),
            'time': get_current_date()
        }
        return render(request, 'dashboard/index.html', context)
    if pu.is_study_adviser(person):
        # Todo: Add another dashboard, or create an extension
        return HttpResponse("You are a study adviser, but your dashboard is yet to be implemented")
    if pu.is_teacher(person):
        # Todo: Add another dashboard, or create an extension
        return HttpResponse("You are a teacher, but your dashboard is yet to be implemented")
    if pu.is_teaching_assistant(person):
        # Todo: Add another dashboard, or create an extension
        return HttpResponse("You are a teaching assistant, but your dashboard is yet to be implemented")
    if pu.is_student(person):
        # Todo: Add another dashboard, or create an extension
        studying = Studying.objects.filter(person=person)
        return redirect('grades:student', studying.get(person__user=request.user).person.id)


@login_required
def modules(request):
    """
    Checks the type of logged in user and directs to view with relevant modules.

    :param request: Django request for authentication
    :return: Redirect to module (edition) overview
    """
    person = Person.objects.get(user=request.user)
    if pu.is_coordinator_or_assistant(person):
        context = {
            'modules': ModuleEdition.objects.filter(coordinator__person=person)
        }
        return render(request, 'dashboard/modules.html', context)
    else:
        # Todo: Add other usertypes
        return PermissionDenied('Other types than coordinator (assistant) are not yet supported')


def student(request):
    return render(request, 'dashboard/student_index.html')


def logged_out(request):
    """
    Logs the user out and directs to logged out portal

    :param request: Django request for authentication
    :return: Redirect to logged out portal
    """
    return render(request, 'registration/success_logged_out.html')


@login_required
def settings(request):
    raise Http404('Settings unimplemented')


def get_modules(person):
    return ModuleEdition.objects.filter(coordinator__person=person).order_by('-start')


def get_current_date():
    return timezone.localdate()


# View renders for the error pages
def server_error(request):
    return render(request, 'errors/500.html', status=500)


def not_found(request):
    return render(request, 'errors/404.html', status=404)


def permission_denied(request):
    return render(request, 'errors/403.html', status=403, )


def bad_request(request):
    return render(request, 'errors/400.html', status=400)
