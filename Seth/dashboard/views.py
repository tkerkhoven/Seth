from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseForbidden, HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

import json

from Grades.models import Module, ModuleEdition, Person, Coordinator, Studying, Grade, ModulePart, Test, Study

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
            context = {
                'modules': self.make_modules_context()['module_editions'],
                'time': get_current_date(),
                'person': Person.objects.filter(user=request.user)[0]
            }
            return render(request, 'dashboard/index.html', context)
        if pu.is_study_adviser(person):
            return redirect('sa_dashboard')
            # return render(request, 'dashboard/sa_index.html')
        if pu.is_teacher(person):
            print(self.make_module_parts_context()['module_parts'])
            context = {
                'module_parts': self.make_module_parts_context()['module_parts'],
                'person': Person.objects.filter(user=request.user)[0]
            }
            return render(request, 'dashboard/teacher_index.html', context)
        if pu.is_teaching_assistant(person):
            print(Person.objects.filter(user=request.user))
            context = {
                'module_parts': self.make_module_parts_context()['module_parts'],
                'person': Person.objects.filter(user=request.user)[0]
            }
            return render(request, 'dashboard/ta_index.html', context)
        if pu.is_student(person):
            studying = Studying.objects.filter(person=person)
            return redirect('grades:student', studying.get(person__user=self.request.user).person.id)
        else:
            return redirect('not_in_seth')

    def make_modules_context(self):
        module_editions = ModuleEdition.objects.filter(coordinator__person__user=self.request.user).prefetch_related(
            'modulepart_set__test_set')
        context = dict()
        context['module_editions'] = []
        num_grades = dict()

        for test in Test.objects.filter(module_part__module_edition__coordinator__person__user=self.request.user).annotate(num_grades=Count('grade__student', distinct=True)):
            num_grades[test] = test.num_grades

        for module_edition in module_editions:
            edition = {'name': module_edition, 'pk': module_edition.pk, 'module_parts': []}
            for module_part in module_edition.modulepart_set.all():
                part = {'name': module_part.name, 'pk': module_part.pk, 'tests': []}
                sign_off_assignments = []
                for test in module_part.test_set.all():
                    if test.type is 'A':
                        sign_off_assignments.append(test)
                        continue

                    test_item = {'name': test.name, 'pk': test.pk, 'signoff': False, 'num_grades': num_grades[test], 'released': test.released}
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
        module_parts = ModulePart.objects.filter(teacher__person__user=self.request.user).prefetch_related(
            'test_set')
        num_grades = dict()

        for test in Test.objects.filter(module_part__teacher__person__user=self.request.user).annotate(num_grades=Count('grade__student', distinct=True)):
            num_grades[test] = test.num_grades

        context = dict()
        context['module_parts'] = []
        for module_part in module_parts:
            part = {'name': module_part.name, 'pk': module_part.pk, 'module_edition': module_part.module_edition, 'tests': []}
            sign_off_assignments = []
            for test in module_part.test_set.all():
                if test.type is 'A':
                    sign_off_assignments.append(test)
                    continue
                test_item = {'name': test.name, 'pk': test.pk, 'signoff': False, 'num_grades': num_grades[test], 'released': test.released}
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
def study_adviser_view(request):
    person = Person.objects.filter(user=request.user).first()
    if not pu.is_study_adviser(person):
        raise PermissionDenied()
    context = dict()
    person = Person.objects.filter(user=request.user).first()
    if pu.is_study_adviser(person):
        inner_qs = Module.objects.filter(study__advisers=person)
        persons = Person.objects.filter(studying__module_edition__module__study__advisers=person) \
            .order_by('university_number', 'user') \
            .distinct('university_number', 'user')
        context['persons'] = persons
        context['module_editions'] = ModuleEdition.objects.filter(module__study__advisers__user=request.user)
        context['studies'] = Study.objects.filter(advisers__user=request.user)
    # else:
        #     Not a study adviser\

    return render(request, 'dashboard/sa_index.html', context)


def filter_students_by_module_edition(request):
    module_edition_pks = json.loads(request.GET.get('module_edition_pks', None))
    person_pks = Person.objects.filter(studying__module_edition__pk__in=module_edition_pks).values_list('pk', flat=True)
    if person_pks.count() == 0:
        empty = True
    else:
        empty = False
    data = {
        'person_pks': json.dumps(list(person_pks)),
        'empty': empty
    }
    return JsonResponse(data)


@login_required
def not_in_seth(request):
    return render(request, 'dashboard/not_in_seth.html')

@login_required
def manual_view(request):
    person = Person.objects.filter(user=request.user).first()
    if pu.is_coordinator_or_assistant(person) or pu.is_study_adviser(person) or pu.is_teacher(person) or pu.is_teaching_assistant(person):
        try:
            return FileResponse(open('manual.pdf', 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            return not_found(request)
    else:
        return permission_denied(request)


def logged_out(request):
    """
    Logs the user out and directs to logged out portal

    :param request: Django request for authentication
    :return: Redirect to logged out portal
    """
    return render(request, 'registration/success_logged_out.html')


def get_persons(person):
    qs = Person.objects.none()


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


def bad_request(request, context):
    return render(request, 'errors/400.html', status=400, context=context)
