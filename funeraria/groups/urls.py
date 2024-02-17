
from django.urls import path
from groups import views
urlpatterns = [
    path('create/', views.create, name='create'),
    path('update/<int:pk>/', views.update, name='update'),
    path('view/<int:pk>/', views.view, name='view'),
    path('remove/<int:pk>/', views.remove, name='remove'),
    path('list/', views.list, name='list')
]