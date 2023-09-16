
from django.urls import path
from stats import views
urlpatterns = [
    path('deaths-per-day/', views.deaths_per_day, name='deaths_per_day'),
    path('templates-per-day/', views.templates_per_day, name='templates_per_day'),
    path('deaths-by-district/', views.deaths_by_district, name='deaths_by_district'),
    path('deaths-by-user/', views.deaths_by_user, name='deaths_by_user'),
]