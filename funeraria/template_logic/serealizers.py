from rest_framework import serializers
from template_logic.models import TemplateLogic

class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateLogic
        fields = ['title','file','group','slug']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('title', 'group'),
                message= "Template title as to be unique in group"
            )
        ]

    