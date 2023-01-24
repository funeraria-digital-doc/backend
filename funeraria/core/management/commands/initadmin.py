from decouple import config
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from decouple import config
class Command(BaseCommand):
    def handle(self, *args, **options):
        username = config('DJANGO_SUPERUSER_USERNAME')
        email = config('DJANGO_SUPERUSER_EMAIL')
        password = config('DJANGO_SUPERUSER_PASSWORD')
        print('-----------------------------432-----------------------------------')
        print(config('DJANGO_SUPERUSER_USERNAME'))
        print(config('DJANGO_SUPERUSER_EMAIL'))
        print(config('DJANGO_SUPERUSER_PASSWORD'))
        print('----------------------------------------------------------------')
        if not User.objects.filter(username=username).exists():
            print('Creating account for %s (%s)' % (username, email))
            admin = User.objects.create_superuser(
                email=email, username=username, password=password)
            print('Created')
        else:
            print('Admin account has already been initialized.')