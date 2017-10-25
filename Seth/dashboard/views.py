from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from Grades.models import ModuleEdition, Person, Coordinator, Studying, Grade, ModulePart, Test

from django.contrib.auth.decorators import login_required
import permission_utils as pu
from django.core.exceptions import PermissionDenied


class DashboardView(View):

    @method_decorator(login_required)
    def dispatch(self, request, **kwargs):
        """
        Checks the type of logged in user and directs to an appropriate dashboard with relevant information.

        :param **kwargs:
        :param request: Django request for authentication
        :return: Redirect to appropriate dashboard (based on type of user)
        """
        person = Person.objects.filter(user=self.request.user).first()

        if pu.is_coordinator_or_assistant(person):
            # print(self.make_modules_context())
            context = {
                'modules': self.make_modules_context()['module_editions'],
                'time': get_current_date()
            }
            return render(request, 'dashboard/index.html', context)
        if pu.is_study_adviser(person):
            return render(request, 'dashboard/sa_index.html')
        if pu.is_teacher(person):
            return render(request, 'dashboard/teacher_index.html')
        if pu.is_teaching_assistant(person):
            return render(request, 'dashboard/ta_index.html')
        if pu.is_student(person):
            studying = Studying.objects.filter(person=person)
            return redirect('grades:student', studying.get(person__user=self.request.user).person.id)
        else:
            return redirect('not_in_seth')

    def make_modules_context(self):
        module_editions = ModuleEdition.objects.filter(coordinator__person__user=self.request.user).prefetch_related(
            'modulepart_set__test_set')
        tests = Test.objects.filter(module_part__module_edition__coordinator__person__user=self.request.user).annotate(num_grades=Count('grade__student', distinct=True))
        context = dict()
        context['module_editions'] = []
        for module_edition in module_editions:
            edition = {'name': module_edition.module.name, 'pk': module_edition.pk, 'module_parts': []}
            for module_part in module_edition.modulepart_set.all():
                part = {'name': module_part.name, 'pk': module_part.pk, 'tests': []}
                sign_off_assignments = []
                for test in module_part.test_set.all():
                    if test.type is 'A':
                        sign_off_assignments.append(test)
                        continue

                    test_item = {'name': test.name, 'pk': test.pk, 'signoff': False, 'num_grades': tests.get(pk=test.pk).num_grades, 'released': test.released}
                    part['tests'].append(test_item)
                if sign_off_assignments:
                    soa_line = {'module_part_pk': module_part.pk, 'signoff': True, 'released': True}
                    if len(sign_off_assignments) > 1:
                        soa_line['name'] =  'S/O assignments {} to {}'.format(sign_off_assignments[0].name,
                                                                  sign_off_assignments[-1].name)
                    else:
                        soa_line['name'] =  'S/O assignment {}'.format(sign_off_assignments[0].name)
                    part['tests'].append(soa_line)
                edition['module_parts'].append(part)

            context['module_editions'].append(edition)
        return context

    def make_module_parts_context(self):
        module_parts =  ModulePart.objects.filter(teacher__person__user=self.request.user).prefetch_related(
            'test_set')
        tests = Test.objects.filter(module_part__teacher__person__user=self.request.user).annotate(num_grades=Count('grade'))

        context = dict()
        context['module_parts'] = []
        for module_part in module_parts:
            part = {'name': module_part.name, 'pk': module_part.pk, 'tests': []}
            sign_off_assignments = []
            for test in module_part.test_set.all():
                if test.type is 'A':
                    sign_off_assignments.append(tests.get(pk=test.pk))
                    continue
                test_item = {'name': test.name, 'pk': test.pk, 'signoff': False, 'num_grades': tests.get(pk=test.pk).num_grades, 'released': test.released}
                part['tests'].append(test_item)
            if sign_off_assignments:
                soa_line = {'module_part_pk': module_part.pk, 'signoff': True, 'released': True}
                if len(sign_off_assignments) > 1:
                    soa_line['name'] =  'S/O assignments {} to {}'.format(sign_off_assignments[0].name,
                                                              sign_off_assignments[-1].name)
                else:
                    soa_line['name'] =  'S/O assignment {}'.format(sign_off_assignments[0].name)
                part['tests'].append(soa_line)
            context['module_parts'].append(part)

        return context

@login_required
def not_in_seth(request):
    return render(request, 'dashboard/not_in_seth.html')

@login_required
def modules(request):
    """
    Checks the type of logged in user and directs to view with relevant modules.

    :param request: Django request for authentication
    :return: Redirect to module (edition) overview
    """
    person = Person.objects.filter(user=request.user).first()
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
