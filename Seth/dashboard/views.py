from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseForbidden
from django.utils import timezone
from Grades.models import Module_ed, Person, Coordinator


# @permission_required('grades.add_grade')
@login_required
def home(request):
    if not Person.objects.filter(user=request.user):
        return redirect('dashboard_student')

    if not Coordinator.objects.filter(person__user=request.user):
        return redirect('grades:student', Person.objects.filter(user=request.user).filter(id_prefix='s')[0].pk)

    context = {
        'modules': get_modules(),
        'time': get_current_date()
    }
    return render(request, 'dashboard/index.html', context)


def modules(request):
    context = {
        'modules': get_modules()
    }
    return render(request, 'dashboard/modules.html', context)

def student(request):
    return render(request, 'dashboard/student_index.html')


def logged_out(request):
    return render(request, 'registration/success_logged_out.html')


def settings(request):
    raise Http404('Settings unimplemented')


def get_modules():
    return Module_ed.objects.order_by('-start')


def get_current_date():
    return timezone.localdate()


def server_error(request):
    return render(request, 'errors/500.html')


def not_found(request):
    return render(request, 'errors/404.html')


def permission_denied(request):
    return render(request, 'errors/403.html')


def bad_request(request):
    return render(request, 'errors/400.html')
