from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    url(r'^$', views.import_index, name='import_index'),
    url(r'^(?P<pk>([0-9]+))$', views.import_module, name='import_module')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
