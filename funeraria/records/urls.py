
from django.urls import path
from records import views
urlpatterns = [
    path('create/', views.create, name='create'),
    path('update/<int:pk>/', views.update, name='update'),
    path('get-record/<int:pk>/', views.view, name='view'),
    path('remove/<int:pk>/', views.remove, name='remove'),
    path('list/', views.list, name='list'),
    path('list-by-status/<str:status>/', views.listByStatus, name='listByStatus'),
    path('update-many-status/', views.updateManyStatus, name='updateManyStatus'),
    
]