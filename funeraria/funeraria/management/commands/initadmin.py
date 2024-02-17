from decouple import config
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os
class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        username =  config('DJANGO_SUPERUSER_USERNAME')
        email =  config('DJANGO_SUPERUSER_EMAIL')
        password =  config('DJANGO_SUPERUSER_PASSWORD')
        if not User.objects.filter(username=username).exists():
            print('Creating account for %s (%s)' % (username, email))
            admin = User.objects.create_superuser(
                email=email, username=username, password=password)
            print('Created')
        else:
            print('Admin account has already been initialized.')