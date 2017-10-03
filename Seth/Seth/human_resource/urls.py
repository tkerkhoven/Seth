from django.conf.urls import url
from . import views

app_name = 'human_resource'
urlpatterns = [
    url(r'^users/$', views.PersonsView.as_view(), name='users'),
    url(r'^user/(?P<pk>([0-9]+))/$', views.PersonDetailView.as_view(), name='user'),
    url(r'^user/(?P<pk>([0-9]+))/update-user/$', views.UpdateUser.as_view(), name="update_user"),
    url(r'^user/(?P<pk>([0-9]+))/remove-user/$', views.DeleteUser.as_view(), name="remove_user"),
    url(r'^users/create-user/$', views.CreatePerson.as_view(), name="create_user"),
]