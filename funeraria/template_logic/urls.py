
from django.urls import path
from template_logic import views
urlpatterns = [
    path('template-upload/', views.template_upload, name='template_upload')
]