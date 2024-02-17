
from django.urls import path
from record_templates import views
urlpatterns = [
    path('<int:pk>/list-templates/', views.get_record_templates, name='get_record_templates'),
]