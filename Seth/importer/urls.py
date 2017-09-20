from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    url(r'^import/$', views.importer, name='importer'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
