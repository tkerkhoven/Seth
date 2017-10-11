from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone

from Grades.models import ModuleEdition, Studying, Person
from Grades.models import ModuleEdition

from django.contrib.auth.decorators import login_required
import permission_utils as pu


# @permission_required('grades.add_grade')
@login_required
def home(request):
    person = Person.objects.get(user=request.user)
    if pu.is_coordinator_or_assistant(person):
        context = {
            'modules': get_modules(),
            'time': get_current_date()
        }
        return render(request, 'dashboard/index.html', context)
    if pu.is_study_adviser(person):
        # Todo: Add another dashboard, or create an extension
        return
    if pu.is_teacher(person):
        # Todo: Add another dashboard, or create an extension
        return
    if pu.is_teaching_assistant(person):
        # Todo: Add another dashboard, or create an extension
        return
    if pu.is_student(person):
        # Todo: Add another dashboard, or create an extension
        studying = Studying.objects.filter(person=person)
        return redirect('grades:student', studying.get(person__user=request.user).person.id)


@login_required
def modules(request):
    context = {
        'modules': get_modules()
    }
    return render(request, 'dashboard/modules.html', context)


def logged_out(request):
    return render(request, 'registration/success_logged_out.html')


@login_required
def settings(request):
    raise Http404('Settings unimplemented')


def get_modules():
    return ModuleEdition.objects.order_by('-start')


def get_current_date():
    return timezone.localdate()


def server_error(request):
    return render(request, 'errors/500.html', status=500)


def not_found(request):
    return render(request, 'errors/404.html', status=404)


def permission_denied(request):
    return render(request, 'errors/403.html', status=403, )


def bad_request(request):
    return render(request, 'errors/400.html', status=400)
