
from django.urls import path
from stats import views
urlpatterns = [
    path('deaths-per-day/', views.deaths_per_day, name='deaths_per_day'),
    path('deaths-per-months/', views.deaths_per_months, name='deaths_per_months'),
    path('deaths-by-district/', views.deaths_by_district, name='deaths_by_district'),
    path('deaths-by-user/', views.deaths_by_user, name='deaths_by_user'),
    path('current-month-services/', views.current_month_services, name='current_month_services'),
    path('current-year-services/', views.current_year_services, name='current_year_services'),
    path('best-month/', views.best_month, name='best_month'),
]