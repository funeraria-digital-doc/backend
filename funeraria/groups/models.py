from django.db import models
from django_currentuser.db.models import CurrentUserField
from django.utils.text import slugify
class Group(models.Model):
    name = models.CharField(max_length=255, unique=True, db_column='name')
    page = models.JSONField(null=True, blank=True)
    slug = models.CharField(max_length=255, blank=True, null=True)
    created_by = CurrentUserField(related_name='group_created_by')
    updated_by = CurrentUserField(related_name='group_updated_by', on_update=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if slugify(self.name) != self.slug:
            self.slug = slugify(self.name)
        super(Group, self).save(*args, **kwargs)


    