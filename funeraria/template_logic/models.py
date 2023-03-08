from django.db import models
from django.template.defaultfilters import slugify
from django_currentuser.db.models import CurrentUserField

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
    created_by = CurrentUserField(related_name='template_created_by')
    updated_by = CurrentUserField(related_name='template_updated_by',on_update=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(TemplateLogic, self).save(*args, **kwargs)


    def __str__(self):
        return self.title

