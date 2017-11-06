from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    url(r'^$', views.DashboardView.as_view(), name='home'),
    url(r'^sa_dashboard/$', views.study_adviser_view, name='sa_dashboard'),
    url(r'^dashboard/$', views.DashboardView.as_view(), name='home'),
    url(r'settings/$', views.settings, name='settings'),
    url(r'^successfully_logged_out/$', views.logged_out, name='logged_out'),
    url(r'^not_in_seth/$', views.not_in_seth, name='not_in_seth'),
    url(r'^filter_students/$', views.filter_students_by_module_edition, name='filter_students'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
