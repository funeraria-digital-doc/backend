from djongo import models
from records.models import Record
from template_logic.models import TemplateLogic
from django_currentuser.db.models import CurrentUserField
class RecordTemplates(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, null=True)
    template = models.ForeignKey(TemplateLogic, on_delete=models.CASCADE, null=True)
    answers = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    created_by = CurrentUserField(related_name='record_template_created_by')
    updated_by = CurrentUserField(related_name='record_template_updated_by',on_update=True)
    objects = models.DjongoManager()

    def __str__(self):
        return self.id