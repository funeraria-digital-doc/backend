from rest_framework import serializers
from template_logic.models import TemplateLogic, Validation, Options
from docxtpl import DocxTemplate


    
class UploadSerializer(serializers.ModelSerializer):
    class ValidationsSerializer(serializers.Serializer):
        class OptionsSerializer(serializers.Serializer):
            class OptionSerializer(serializers.Serializer):
                label = serializers.CharField()
                value = serializers.CharField()
                
                class Meta:
                    model = Options
                    fields = "__all__"

            options = serializers.ListField(allow_empty=True, child = OptionSerializer())
            variable_type = serializers.CharField()
            
            class Meta:
                model = Options
                fields = "__all__"

        name = serializers.CharField()
        optional = serializers.BooleanField(required=False)
        options = OptionsSerializer(allow_null=True,required = False)
        field_type = serializers.CharField()
        placeholder = serializers.CharField(required = False)
        format = serializers.CharField(required = False,allow_blank=True)
        label = serializers.CharField(required = False,allow_blank=True)
        class Meta:
            model = Validation
            fields = ['name', 'optional', 'options', 'field_type', 'placeholder','format','label']

        
    validations = serializers.ListField(allow_empty=True, child = ValidationsSerializer())
    class Meta:
        model = TemplateLogic
        fields = ['title','file','group','slug','validations']
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
    validations = serializers.JSONField(required = False)
    class Meta:
        model = TemplateLogic
        fields = ['title','file','group','slug','validations']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('title', 'group'),
                message= "Template title as to be unique in group"
            ),
        ]




