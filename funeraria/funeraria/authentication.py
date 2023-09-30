from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.timezone import now
import hashlib
import logging
logger = logging.getLogger(__name__)
class CachingTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        authorization_header = request.headers.get('Authorization', '')
        if not authorization_header.startswith('Bearer '):
            return None
        
        def hash_token(token):
            return hashlib.sha256(token.encode('utf-8')).hexdigest()
        
        raw_token = authorization_header[len('Bearer '):].strip()
        cache_key = f"auth-{hash_token(raw_token)}"
        user_auth_tuple = cache.get(cache_key)
        if user_auth_tuple is None:
            user_auth_tuple = super().authenticate(request)
            if user_auth_tuple is not None:
                cache.set(cache_key, user_auth_tuple)
        else:
            cache.touch(cache_key)

        if int(user_auth_tuple[1].get('exp')) < int((now()).timestamp()):
            cache.delete(cache_key)
            raise AuthenticationFailed("Token has expired")
        return user_auth_tuple