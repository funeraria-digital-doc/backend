from rest_framework import serializers
from template_logic.models import TemplateLogic
from docxtpl import DocxTemplate

class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateLogic
        fields = ['title','file','group','slug','validators']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('title', 'group'),
                message= "Template title as to be unique in group"
            )
        ]



class EditSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required = False)
    group = serializers.IntegerField(required = False)
    slug = serializers.CharField(required = False)
    file = serializers.FileField(required = False)
    validators = serializers.JSONField(required = False)
    class Meta:
        model = TemplateLogic
        fields = ['title','file','group','slug','validators']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('title', 'group'),
                message= "Template title as to be unique in group"
            ),
        ]




