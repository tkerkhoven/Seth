from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from Grades.models import ModuleEdition
import permission_utils as pu


# @permission_required('grades.add_grade')
def home(request):
    context = {
        'modules': get_modules(),
        'time': get_current_date(),
        'permissions': {'mc': pu.is_module_coordinator(request.user),
                        'ta': pu.is_teaching_assistant(request.user),
                        'tc': pu.is_teacher(request.user),
                        'ad': pu.is_study_adviser(request.user),
                        'st': pu.is_student(request.user),
                        'mca':pu.is_module_coordinator_assistant(request.user)
                        }
        # [
        #     {
        #         'name': 'Pearls of Computer Science',
        #         'courses': [
        #             {
        #                 'name': 'Pearl 1',
        #             }
        #         ]
        #     }
        # ],
    }
    print(context)
    return render(request, 'dashboard/index.html', context)


def modules(request):
    context = {
        'modules': get_modules(),
    }
    return render(request, 'dashboard/modules.html', context)


def logged_out(request):
    return render(request, 'registration/success_logged_out.html')


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
    return render(request, 'errors/403.html', status=403)


def bad_request(request):
    return render(request, 'errors/400.html', status=400)
