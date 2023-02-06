
from django.urls import path, include
from accounts import views
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    path('register/', views.registration, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile')
]