from django.conf.urls import url
from . import views

app_name = 'grades'
urlpatterns = [
    url(r'^$', views.ModuleView.as_view(), name='modules'),
    url(r'^(?P<pk>([0-9]+))/$', views.GradeView.as_view(), name='gradebook'),
    url(r'^(?P<pk>([0-9]+)?P<sid>([0-9]+))/$', views.StudentView.as_view(), name='student'),
    url(r'^users/$', views.PersonsView.as_view(), name='users'),
    url(r'^user/(?P<pk>([0-9]+))/$', views.PersonDetailView.as_view(), name='user'),
    url(r'^user/(?P<pk>([0-9]+))/update-user/$', views.UpdateUser.as_view(), name="update_user"),
    url(r'^user/(?P<pk>([0-9]+))/remove-user/$', views.DeleteUser.as_view(), name="remove_user"),
    url(r'^users/create-user/$', views.CreatePerson.as_view(), name="create_user"),
    url(r'^$', views.ModuleView.as_view(), name='modules'),
    url(r'^modules/(?P<pk>([0-9]+))/$', views.GradeView.as_view(), name='gradebook'),
    url(r'^modules/(?P<pk>([0-9]+))/(?P<sid>([0-9]+))/$', views.ModuleStudentView.as_view(), name='modstudent'),
    url(r'^students/(?P<pk>([0-9]+))/$', views.StudentView.as_view(), name='student'),
    url(r'^courses/(?P<pk>([0-9]+))/$', views.CourseView.as_view(), name='course'),
    url(r'^tests/(?P<pk>[0-9]+)/$', views.TestView.as_view(), name='test'),
    url(r'^exports/(?P<pk>([0-9]+))/$', views.export, name='export'),
    url(r'^release/(?P<pk>([0-9]+))/$', views.release, name='release'),
    url(r'^retract/(?P<pk>([0-9]+))/$', views.release, name='retract'),
]
