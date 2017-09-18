from django.conf.urls import url

from . import views

app_name = 'module_management'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index')
]
