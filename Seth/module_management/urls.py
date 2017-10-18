from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'module_management'
urlpatterns = [
    url(r'^$', login_required(views.ModuleListView.as_view()), name='module_overview'),
    url(r'^(?P<pk>.+)/module_detail$', login_required(views.ModuleDetailView.as_view()), name='module_detail'),
    url(r'^(?P<pk>.+)/module_edition_detail$', login_required(views.ModuleEditionDetailView.as_view()), name='module_edition_detail'),
    url(r'^(?P<pk>.+)/module_edition_update$', login_required(views.ModuleEditionUpdateView.as_view()), name='module_edition_update'),
    url(r'^(?P<pk>.+)/module_edition_create$', login_required(views.ModuleEditionCreateView.as_view()), name='module_edition_create'),
    url(r'^(?P<pk>.+)/module_part_detail$', login_required(views.ModulePartDetailView.as_view()), name='module_part_detail'),
    url(r'^(?P<pk>.+)/module_part_update$', login_required(views.ModulePartUpdateView.as_view()), name='module_part_update'),
    url(r'^(?P<pk>.+)/module_part_create$', login_required(views.ModulePartCreateView.as_view()), name='module_part_create'),
    url(r'^(?P<pk>.+)/module_part_delete$', login_required(views.ModulePartDeleteView.as_view()), name='module_part_delete'),
    url(r'^(?P<pk>.+)/test_detail$', login_required(views.TestDetailView.as_view()), name='test_detail'),
    url(r'^(?P<pk>.+)/test_update$', login_required(views.TestUpdateView.as_view()), name='test_update'),
    url(r'^(?P<pk>.+)/test_create$', login_required(views.TestCreateView.as_view()), name='test_create'),
    url(r'^(?P<pk>.+)/test_delete$', login_required(views.TestDeleteView.as_view()), name='test_delete'),
    url(r'(?P<spk>.+)/(?P<mpk>.+)/user_delete$', login_required(views.remove_user), name='user_delete')
]
