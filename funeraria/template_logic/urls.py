
from django.urls import path
from template_logic import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('list/', views.list_templates, name='list_templates'),
    #path('profile/', views.profile_view, name='profile_view'),
    path('list-group-templates/', views.list_group_templates, name='list_group_templates'),
    path('upload/', views.upload, name='upload'),
    path('get-variables-from-file/', views.get_variables_from_file, name='get_variables_from_file'),
    path('<template_pk>/download/', views.template_download, name='template_download'),
    path('<template_pk>/download/<record_pk>/', views.download, name='download'),
    path('edit/<pk>/', views.edit, name='edit'),
    path('remove/<pk>/', views.remove, name='remove'),
    path('get-variables/<pk>/', views.get_variables, name='get_variables'),
    path('get-template/<pk>/', views.get_template, name='get_template'),
    path('<pk>/get-validations/', views.get_validations, name='get_validations'),
    path('<pk>/check-validations/', views.check_validations, name='check_validations'),
    path('sendTestMail/', views.sendTestMail, name='sendTestMail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)