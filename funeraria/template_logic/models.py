from djongo import models
from django.template.defaultfilters import slugify
from django_currentuser.db.models import CurrentUserField

from groups.models import Group
def get_upload_path(instance, filename):
    if instance.group is not None:
        return instance.group.name + '/' + filename
    return '/' + filename

class FieldType(models.TextChoices):
        TEXT = "Text"
        BOOLEAN = "Boolean"
        INTEGER = "Integer"
        SELECT = "Select"
        TEXTAREA = "Text Area"
        RADIO = "Radio"
        CHECKBOX = "Checkbox"
        DATE = "Date"
        DATETIME = "DateTime"

class Option(models.Model):
    value = models.CharField(max_length=128)

    class Meta:
        abstract = True

class Validation(models.Model):
    name = models.CharField(max_length=128)
    optional = models.BooleanField(default=True)
    options = models.EmbeddedField(
        model_container=Option
    )
    field_type = models.CharField(max_length=64, choices=FieldType.choices,  db_column='field_type')
    placeholder = models.CharField(max_length=64)
    format = models.CharField(max_length=32)

    class Meta:
        abstract = True

class TemplateLogic(models.Model):
    title = models.CharField(max_length=255, null=False)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=get_upload_path, null=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    validations = models.EmbeddedField(
        model_container=Validation
    ) 
    created_by = CurrentUserField(related_name='template_created_by')
    updated_by = CurrentUserField(related_name='template_updated_by',on_update=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(TemplateLogic, self).save(*args, **kwargs)


    def __str__(self):
        return self.title

