from io import BytesIO
import logging
import os
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_currentuser.db.models import CurrentUserField
from PIL import Image
from django.core.files.base import ContentFile
from groups.models import Group
logger = logging.getLogger(__name__)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def get_upload_path(instance, filename):
    # Customize the upload path and filename if needed
    folder_path = 'accounts/' + instance.username
    full_path = os.path.join(folder_path, instance.username + "_picture.jpg")
     # Remove the existing image file if it exists
    if os.path.exists(full_path):
        os.remove(full_path)
    return full_path

class User(AbstractUser):
    class Status(models.TextChoices):
        INACTIVE = "1", "Inactive"
        ACTIVE = "2", "Active"
        SUSPENDED = "3", "Suspended"

    group_user = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=64, choices=Status.choices, blank=True,default=Status.ACTIVE) 
    file = models.ImageField(upload_to=get_upload_path)
    created_by = CurrentUserField(related_name='account_created_by')
    updated_by = CurrentUserField(related_name='account_updated_by',on_update=True)
    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Check if the instance already exists in the database
        if self.pk:
            # Retrieve the existing instance from the database
            old_instance = User.objects.get(pk=self.pk)
            # Check if the image field has changed
            if old_instance.file != self.file:
                # Delete the previous image file
                old_instance.file.delete(False)
            try:
                img = Image.open(self.file)
                new_size = (800, 600)
                img.thumbnail(new_size)
                # Create a new file buffer to save the optimized image
                new_image_buffer = BytesIO()
                img.save(new_image_buffer, format='JPEG', optimize=True)
                # Create a ContentFile from the buffer
                optimized_image = ContentFile(new_image_buffer.getvalue(),self.username + "_picture")
                # Close the Pillow image
                img.close()
                self.file = optimized_image
            except Exception as e:
                logger.info("save image error")
                logger.info(e)
            
        super().save(*args, **kwargs)
    