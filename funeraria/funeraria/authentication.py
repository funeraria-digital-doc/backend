from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.timezone import now
import logging
logger = logging.getLogger(__name__)
class CachingTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        authorization_header = request.headers.get('Authorization', '')
        if not authorization_header.startswith('Bearer '):
            return None
        user_auth_tuple = super().authenticate(request)

        if int(user_auth_tuple[1].get('exp')) < int((now()).timestamp()):
            raise AuthenticationFailed("Token has expired")
        return user_auth_tuple