
from django.urls import path, include
from accounts import views
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    path('register/', views.registration, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('create-superuser/', views.create_superuser, name='create_superuser'),
    path('create-staffuser/', views.create_staffuser, name='create_staffuser'),
    path('remove/<int:pk>', views.remove, name='remove'),
    path('profile-admin/<int:pk>', views.profile_admin, name='profile_admin'),
    path('edit-profile-admin/<int:pk>', views.edit_profile_admin, name='edit_profile_admin'),
]