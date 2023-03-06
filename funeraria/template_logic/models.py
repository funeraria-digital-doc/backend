from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.urls import reverse

from groups.models import Group
def get_upload_path(instance, filename):
    if instance.group is not None:
        return instance.group.name + '/' + filename
    return '/' + filename


class TemplateLogic(models.Model):
    title = models.CharField(max_length=255, null=False)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=get_upload_path, null=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(TemplateLogic, self).save(*args, **kwargs)


    def __str__(self):
        return self.title

