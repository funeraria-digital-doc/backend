from rest_framework import authentication
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
class BearerAuthentication(authentication.TokenAuthentication):
    keyword = 'Token'


User = get_user_model()
class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email')
        if email is None:
            logger.info(f'EmailBackend.authenticate: email is None')
            email = username
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
