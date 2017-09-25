from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.http import Http404
from django.utils import timezone
from Grades.models import Module, Course, Module_ed, Test

import time
import datetime

# @permission_required('grades.add_grade')
def home(request):
    context = {
        'modules': get_modules(),
        'time': get_current_date()
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
    return render(request, 'dashboard/index.html', context)

def logged_out(request):
    return render(request, 'registration/success_logged_out.html')

def settings(request):
    raise Http404('Settings unimplemented')

def get_modules():
    return Module_ed.objects.order_by('module__name')

def get_current_date():
    return timezone.localdate()
