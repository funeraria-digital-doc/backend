from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from template_logic.models import TemplateLogic


class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateLogic
        fields = ['title','file']
        validators = [
            
        ]

    