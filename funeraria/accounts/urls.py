
from django.urls import path
from accounts import views
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('create-user/', views.create_new_user, name='create_new_user'),
    path('profile-image/', views.profile_image, name='profile_image'),
    path('change-password/', views.change_password, name='change_password'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('file-upload/', views.file_upload, name='file_upload'),
    path('list-all-users/', views.list_all_users, name='list_all_users'),
    path('remove/<int:pk>/', views.remove, name='remove'),
    path('edit-user/<int:pk>/', views.edit_user, name='edit_user'),
]