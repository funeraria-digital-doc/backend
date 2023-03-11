
from django.urls import path
from template_logic import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('list/', views.list_templates, name='list_templates'),
    path('upload/', views.upload, name='upload'),
    path('download/<pk>', views.download, name='download'),
    path('edit/<pk>', views.edit, name='edit'),
    path('remove/<pk>', views.remove, name='remove'),
    path('get-variables/<pk>', views.get_variables, name='get_variables'),
    path('edit-variables/<pk>', views.edit_variables, name='edit_variables'),
    path('<pk>/get-validations', views.get_validations, name='get_validations'),
    # path('edit-variables/<pk>', views.edit_variables, name='edit_variables')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)