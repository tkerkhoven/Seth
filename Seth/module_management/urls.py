from django.conf.urls import url

from . import views

app_name = 'module_management'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='module_overview'),
    url(r'^(?P<pk>.+)/module_detail$', views.ModuleView.as_view(), name='module_detail'),
    url(r'^(?P<pk>.+)/module_ed_detail$', views.ModuleEdView.as_view(), name='module_ed_detail')
]
