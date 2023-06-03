
from django.urls import path, include
from records import views
urlpatterns = [
    path('create/', views.create, name='create'),
    path('update/<int:pk>/', views.update, name='update'),
    path('view/<int:pk>/', views.view, name='view'),
    path('<int:pk>/', views.remove, name='remove'),
    path('list/', views.list, name='list'),
]