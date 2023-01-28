from getpass import getuser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.signals import user_logged_in

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        print(instance)
        Token.objects.create(user=instance)


@receiver(user_logged_in, sender=settings.AUTH_USER_MODEL)
def userLogIn(sender, instance=None, created=False, **kwargs):
    print('just logged in')
    