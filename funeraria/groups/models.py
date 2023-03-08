from django.db import models
from django_currentuser.db.models import CurrentUserField

class Group(models.Model):
    name = models.CharField(max_length=255,unique=True, db_column='name') 
    created_by = CurrentUserField(related_name='group_created_by')
    updated_by = CurrentUserField(related_name='group_updated_by',on_update=True)
    
    def __str__(self):
        return self.name


    