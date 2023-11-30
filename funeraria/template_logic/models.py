from djongo import models
from django_currentuser.db.models import CurrentUserField
from groups.models import Group
import logging
logger = logging.getLogger(__name__)
class TemplateLogic(models.Model):
    title = models.CharField(max_length=255, null=True)
    file = models.CharField(max_length=10000000, null=True)
    file_name = models.CharField(max_length=1024,null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    validations = models.JSONField(null=True, blank=True)
    file_validations = models.JSONField(null=True, blank=True)
    send_type = models.CharField(max_length=255,null=True, blank=True, default="NONE")
    send_email_to = models.JSONField()
    send_email_to_cc = models.JSONField()
    send_email_to_bcc = models.JSONField()
    created_by = CurrentUserField(related_name='template_created_by') # type: ignore
    updated_by = CurrentUserField(related_name='template_updated_by',on_update=True) # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    objects = models.DjongoManager()

    def __str__(self):
        return self.title
    
