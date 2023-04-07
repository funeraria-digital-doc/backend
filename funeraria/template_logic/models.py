from djongo import models
from django.template.defaultfilters import slugify
from django_currentuser.db.models import CurrentUserField

from groups.models import Group
def get_upload_path(instance, filename):
    if instance.group is not None:
        return instance.group.name + '/' + filename
    return '/' + filename

class SendEmailTo(models.Model):
    to = models.EmailField(max_length=255)
    class Meta:
        abstract = True

class TemplateLogic(models.Model):
    title = models.CharField(max_length=255, null=False)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=get_upload_path, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    validations = models.JSONField()
    send_type = models.CharField(max_length=255,null=True, blank=True, default="NONE")
    send_email_to = models.JSONField(models.EmailField(max_length=255), null=True, blank=True)
    send_email_to_cc = models.JSONField(models.EmailField(max_length=255), null=True, blank=True)
    send_email_to_bcc = models.JSONField(models.EmailField(max_length=255), null=True, blank=True)
    created_by = CurrentUserField(related_name='template_created_by') # type: ignore
    updated_by = CurrentUserField(related_name='template_updated_by',on_update=True) # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(TemplateLogic, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.title


