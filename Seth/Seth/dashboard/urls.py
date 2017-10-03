from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^dashboard/$', views.home, name='home'),
    url(r'settings/$', views.settings, name='settings'),
    url(r'^successfully_logged_out/$', views.logged_out, name='logged_out'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
