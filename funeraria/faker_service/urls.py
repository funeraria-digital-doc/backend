
from django.urls import path
from faker_service import views
urlpatterns = [
    path('create-record/', views.create_record, name='create_record'),
    path('create-group-with-users/', views.create_group_with_users, name='create_group_with_users'),
    path('create-templates/', views.create_templates, name='create_templates'),
]