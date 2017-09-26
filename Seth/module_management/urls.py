from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'module_management'
urlpatterns = [
    url(r'^$', login_required(views.IndexView.as_view()), name='module_overview'),
    url(r'^(?P<pk>.+)/module_detail$', login_required(views.ModuleView.as_view()), name='module_detail'),
    url(r'^(?P<pk>.+)/module_ed_detail$', login_required(views.ModuleEdView.as_view()), name='module_ed_detail'),
    url(r'^(?P<pk>.+)/course_detail$', login_required(views.CourseView.as_view()), name='course_detail'),
    url(r'^(?P<pk>.+)/test_detail$', login_required(views.TestView.as_view()), name='test_detail'),
    url(r'^(?P<pk>.+)/module_ed_update$', login_required(views.ModuleEdUpdateView.as_view()), name='module_ed_update'),
    url(r'^(?P<pk>.+)/course_update$', login_required(views.CourseUpdateView.as_view()), name='course_update'),
    url(r'^(?P<pk>.+)/test_update$', login_required(views.TestUpdateView.as_view()), name='test_update')
]
