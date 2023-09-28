from django.core.cache import cache
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.timezone import localtime
from datetime import timedelta
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)
class CachingTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        # Check if the authentication result is in the cache
        cache_key = f"auth-{key}"
        user_auth_tuple = cache.get(cache_key)
        if user_auth_tuple is None:
            # If the result is not in the cache, call the parent implementation
            user_auth_tuple = super().authenticate_credentials(key)
            # Store the result in the cache for future use
            cache.set(cache_key, user_auth_tuple)
        else: 
            cache.touch(cache_key)

        if localtime(user_auth_tuple[1].created) < localtime(timezone.now() - timedelta(hours=24)):
            cache.delete(cache_key)
            user_auth_tuple[0].auth_token.delete()
            raise AuthenticationFailed("Token has expired")
        return user_auth_tuple