from django.urls import path
from django.conf.urls import url, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from user_app.api.views import registration_view, logout_view


urlpatterns = [
    path('/', include('rest_auth.urls')),
    path('/registration/', include('rest_auth.registration.urls')),
    #path('register/', registration_view, name='register'),
    # path('login/', obtain_auth_token, name='login'),
    # path('logout/', logout_view, name='logout'),
    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('refresh-login/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('token-verify/', TokenVerifyView.as_view(), name='token_verify'),
]