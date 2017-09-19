from django.conf.urls import url
from . import views

app_name = 'grades'
urlpatterns = [
	url(r'^$', views.ModuleView.as_view(), name='modules'),
    url(r'^modules/(?P<pk>([0-9]+))/$', views.GradeView.as_view(), name='gradebook'),
    url(r'^modules/(?P<pk>([0-9]+))/(?P<sid>([0-9]+))/$', views.ModuleStudentView.as_view(), name='modstudent'),
    url(r'^students/(?P<pk>([0-9]+))/$', views.StudentView.as_view(), name='student'),
]