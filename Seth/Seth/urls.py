from django.conf import settings
from django.conf.urls.static import static


"""Seth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('dashboard.urls')),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^importer/', include('importer.urls')),
    url(r'^grades/', include('Grades.urls')),
    url(r'^module_management/', include('module_management.urls')),
    url(r'^human_resource/', include('human_resource.urls'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

handler404 = 'dashboard.views.not_found'
handler500 = 'dashboard.views.server_error'
handler403 = 'dashboard.views.permission_denied'
handler400 = 'dashboard.views.bad_request'
