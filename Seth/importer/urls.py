from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='import_index'),
    url(r'module/(?P<pk>[0-9]+)', views.import_module, name='import_module'),
    url(r'test/(?P<pk>[0-9]+)', views.import_test, name='import_test'),
    url(r'import-new-student', views.import_student, name='import_new_student'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
