from django.conf import settings


def installed_apps(request):
    return {
        'grades_installed': 'Grades.apps.GradesConfig' in settings.INSTALLED_APPS,
        'importer_installed': 'importer' in settings.INSTALLED_APPS,
        'hr_installed': 'Grades.apps.GradesConfig' in settings.INSTALLED_APPS,
    }
