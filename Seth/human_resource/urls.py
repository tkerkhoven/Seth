from django.conf.urls import url
from . import views

app_name = 'human_resource'
urlpatterns = [
    url(r'^users/$', views.PersonsView.as_view(), name='persons'),
    url(r'^user/(?P<pk>([0-9]+))/$', views.PersonDetailView.as_view(), name='person'),
    url(r'^user/(?P<pk>([0-9]+))/update-person/$', views.UpdatePerson.as_view(), name="update_person"),
    url(r'^user/(?P<pk>([0-9]+))/remove-person/$', views.DeletePerson.as_view(), name="remove_person"),
    url(r'^users/create-person/$', views.CreatePersonNew.as_view(), name="create_person"),
]
