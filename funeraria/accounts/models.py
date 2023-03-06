from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from django.db import models

from groups.models import Group
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)




class User(AbstractUser):
    class Status(models.TextChoices):
        INACTIVE = "1", "Inactive"
        ACTIVE = "2", "Active"
        SUSPENDED = "3", "Suspended"

    group_user = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=64, choices=Status.choices, blank=True,default=Status.ACTIVE) 
    def __str__(self):
        return self.username
    