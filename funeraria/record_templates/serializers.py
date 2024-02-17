from template_logic.models import TemplateLogic
from record_templates.models import RecordTemplates
from records.models import Record
from rest_framework import serializers

import logging
logger = logging.getLogger(__name__)

class RecordTemplateSerializer(serializers.ModelSerializer):
    
    template = serializers.PrimaryKeyRelatedField(required = False, allow_null = True, queryset = TemplateLogic.objects.all())
    record = serializers.PrimaryKeyRelatedField(required = False, allow_null = True, queryset = Record.objects.all())
    answers = serializers.ListField(allow_empty=True, allow_null = True, required= False)
    
    class Meta:
        model = RecordTemplates
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']
        