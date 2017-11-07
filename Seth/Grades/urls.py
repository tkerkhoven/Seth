from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'grades'
urlpatterns = [
    url(r'^$', login_required(views.ModuleView.as_view()), name='modules'),
    url(r'^$', login_required(views.ModuleView.as_view()), name='modules'),
    url(r'^modules/(?P<pk>([0-9]+))/$', login_required(views.GradeView.as_view()), name='gradebook'),
    url(r'^modules/(?P<pk>([0-9]+))/(?P<sid>([0-9]+))/$', login_required(views.ModuleStudentView.as_view()), name='modstudent'),
    url(r'^students/(?P<pk>([0-9]+))/$', login_required(views.StudentView.as_view()), name='student'),
    url(r'^module-part/(?P<pk>([0-9]+))/$', login_required(views.ModulePartView.as_view()), name='module_part'),
    url(r'^tests/(?P<pk>[0-9]+)/$', login_required(views.TestView.as_view()), name='test'),
    url(r'^tests/(?P<pk>[0-9]+)/send_email$', login_required(views.EmailGradeReleasedPreviewView.as_view()), name='test_send_email'),
    url(r'^exports/(?P<pk>([0-9]+))/$', login_required(views.export), name='export'),
    url(r'^release/(?P<pk>([0-9]+))/$', login_required(views.release), name='release'),
    url(r'^release/$', login_required(views.bulk_release), name='bulk-release'),
    url(r'^remove/(?P<pk>([0-9]+))/(?P<sid>([0-9]+))/$', login_required(views.remove), name='remove'),
    url(r'^edit/(?P<pk>([0-9]+))/(?P<sid>([0-9]+))/$', login_required(views.edit), name='edit'),
    url(r'^get/(?P<pk>([0-9]+))/(?P<t>([AE]))$', login_required(views.get), name='get'),
]