from django.forms import ValidationError
from rest_framework import serializers
from accounts.models import User
from groups.models import Group
from records.models import Record
from template_logic.models import TemplateLogic
from docxtpl import DocxTemplate
from json import JSONDecoder



FIELD_TYPE_CHOICES =(
    ("BOOLEAN",'BOOLEAN'), 
    ("INTEGER",'INTEGER'), 
    ("SELECT","SELECT"), 
    ("MULTISELECT","MULTISELECT"), 
    ("TEXT",'TEXT'), 
    ("TEXTAREA","TEXTAREA"), 
    ("RADIO","RADIO"), 
    ("CHECKBOX","CHECKBOX"), 
    ("DATE","DATE"), 
    ("DATETIME","DATETIME"), 
    ("TIME","TIME"),
    ("YEAR","YEAR"),
    ("MONTH","MONTH"),
    ("DAY","DAY"),
    #("FILE","FILE"),
    ("EMAIL","EMAIL")
)

FORMAT_CHOICES = (
    ("HOURS_ONLY",'Hours only'), 
    ("MINUTES_ONLY",'Minutes only'), 
    ("SECONDS_ONLY",'Seconds only'), 
    ("HOURS_MINUTES_SECONDS",'Hours, minutes and seconds'), 
    ("HOURS_MINUTES",'Hours and minutes'), 
    ("MINUTES_SECONDS",'Minutes and seconds'), 
    ("DAY_MONTH_YEAR",'Day, month and year'),  
    ("MONTH_YEAR",'Month and year'),
    ("DAY_MONTH",'Day and Month'),
    ("DAY_MONTH_YEAR_HOUR_MINUTE_SECOND",'Day, month, year, hour, minute and second'),  
    ("DAY_MONTH_YEAR_HOUR_MINUTE",'Day, month, year, hour and minute'),  
    ("DAY_MONTH_YEAR_HOUR",'Day, month, year and hour'),  
    ("DAY_MONTH_HOUR_MINUTE_SECOND",'Day, month, hour, minute and second'),  
    ("DAY_MONTH_HOUR_MINUTE",'Day, month, hour and minute'),  
    ("DAY_MONTH_HOUR",'Day, month and hour'),
    ("MONTH_YEAR_HOUR_MINUTE_SECOND",'Month, year, hour, minute and second'),  
    ("MONTH_YEAR_HOUR_MINUTE",'Month, year, hour and minute'),  
    ("MONTH_YEAR_HOUR",'Month, year and hour')
)


VARIABLE_TYPE_CHOICES = (
    ("STRING",'String'), 
    ("INTEGER",'Integer'), 
    ("FLOAT",'Float'), 
    ("DECIMAL",'Decimal'), 
    ("DATE",'Date'), 
    ("DATETIME",'Datetime'), 
    ("TIME",'Time'), 
    ("BOOLEAN",'Boolean'),  
    ("JSON",'Json'),
    ("ARRAY",'Array'),
)

DEFAULT_VARIABLE_TYPE_CHOICES = (
    ("STRING",'String'), 
    ("INTEGER",'Integer'), 
    ("BOOLEAN",'Boolean')
)


DB_COLLECTION_CHOICES = (
    ("RECORDS",'Records'), 
    ("USERS",'Users'), 
    ("GROUPS",'Groups')
)

SEND_TYPE_CHOICES = (
    ('NONE','NONE'), 
    ('DOCUMENT','Document'), 
    ('EMAIL','Email'),
    ('DOCUMENT_EMAIL','Document and Email')
) 



class UploadSerializer(serializers.ModelSerializer):
    class ValidationsSerializer(serializers.Serializer):
        class OptionsSerializer(serializers.Serializer):
            class OptionSerializer(serializers.Serializer):
                label = serializers.CharField()
                value = serializers.CharField()
                class Meta:
                    fields = ['label','value']

            options = serializers.ListField(allow_empty=True, allow_null=True, child = OptionSerializer())
            variable_type = serializers.ChoiceField(choices = VARIABLE_TYPE_CHOICES)
            
            class Meta:
                fields = ['options','variable_type']

        class DefaultFieldSerializer(serializers.Serializer):

            value = serializers.CharField()
            variable_type = serializers.ChoiceField(choices = DEFAULT_VARIABLE_TYPE_CHOICES)
            
            class Meta:
                fields = ['value','variable_type']

        name = serializers.CharField()
        optional = serializers.BooleanField()
        options = OptionsSerializer(allow_null=True,required = False)
        field_type = serializers.ChoiceField(choices = FIELD_TYPE_CHOICES)
        placeholder = serializers.CharField(required = False)
        format = serializers.ChoiceField(required=False,allow_null = True, allow_blank = True,choices = FORMAT_CHOICES)
        #is_date_numerica true = escrever por extenso
        is_date_numeric = serializers.BooleanField(allow_null = True, required=False)
        label = serializers.CharField(required = False,allow_blank=True)
        is_field_custom = serializers.BooleanField()
        db_collection = serializers.ChoiceField(choices = DB_COLLECTION_CHOICES, allow_null=True, required = False)
        db_field_reference = serializers.CharField(required = False,allow_blank=True)
        min = serializers.IntegerField(required = False)
        max = serializers.IntegerField(required = False)
        default_value = DefaultFieldSerializer(required=False,allow_null= True)

        def validate(self, data):
            data_dict = dict(data)
            data_keys = data.keys()
            field_type= data_dict.get('field_type')
            is_field_custom= data_dict.get('is_field_custom')
            validation_errors = {}
            if field_type in ["DATE","DATETIME","TIME"] and ('format' not in data_keys or data_dict.get('format') == ""):
                validation_errors['format'] = ['When field_type is DATE, DATETIME or TIME, the field format is required.']
            if field_type in ["DATE","DATETIME","TIME"] and ('is_date_numeric' not in data_keys or data_dict.get('is_date_numeric') == ""):
                validation_errors['is_date_numeric'] = ['When field_type is DATE, DATETIME or TIME, the field is_date_numeric is required.']
            if field_type in ["DATE"] and data_dict.get('format') not in ["DAY_MONTH_YEAR","MONTH_YEAR","DAY_MONTH"]:
                validation_errors['format'] = ['When field_type is DATE, format can be DAY_MONTH_YEAR, MONTH_YEAR or DAY_MONTH.']
            if field_type in ["TIME"] and data_dict.get('format') not in ["HOURS_ONLY","MINUTES_ONLY","SECONDS_ONLY","HOURS_MINUTES_SECONDS","HOURS_MINUTES","MINUTES_SECONDS"]:
                validation_errors['format'] = ['When field_type is TIME, format can be HOURS_ONLY, MINUTES_ONLY, SECONDS_ONLY, HOURS_MINUTES_SECONDS, HOURS_MINUTES or MINUTES_SECONDS.']
            if field_type in ["DATETIME"] and data_dict.get('format') not in ["DAY_MONTH_YEAR_HOUR_MINUTE_SECOND","DAY_MONTH_YEAR_HOUR_MINUTE","DAY_MONTH_YEAR_HOUR","DAY_MONTH_HOUR_MINUTE_SECOND","DAY_MONTH_HOUR_MINUTE","DAY_MONTH_HOUR","MONTH_YEAR_HOUR_MINUTE_SECOND","MONTH_YEAR_HOUR_MINUTE","MONTH_YEAR_HOUR"]:
                validation_errors['format'] = ['When field_type is DATETIME, format can be DAY_MONTH_YEAR_HOUR_MINUTE_SECOND, DAY_MONTH_YEAR_HOUR_MINUTE, DAY_MONTH_YEAR_HOUR, DAY_MONTH_HOUR_MINUTE_SECOND, DAY_MONTH_HOUR_MINUTE, DAY_MONTH_HOUR, MONTH_YEAR_HOUR_MINUTE_SECOND, MONTH_YEAR_HOUR_MINUTE, MONTH_YEAR_HOUR.']
            if field_type in ["SELECT","MULTISELECT", "RADIO"] and ('options' not in data_keys or data_dict.get('options') is None):
                validation_errors['options'] = ['When field_type is SELECT, MULTISELECT or RADIO, the field options is required.']
            if field_type in ["SELECT","MULTISELECT", "RADIO"] and data_dict.get('optional') and ('min' not in data_keys or data_dict.get('min') == 0):
                validation_errors['min'] = ['When field of the  SELECT, MULTISELECT or RADIO is not optional, Field min is required.']
            if not is_field_custom and ('db_field_reference' not in data_keys or data_dict.get('db_field_reference') == ""):
                validation_errors['db_field_reference'] = ['If is_field_custom is selected , db_field_reference is required.']
            if not is_field_custom and ('db_collection' not in data_keys or data_dict.get('db_collection') == ""):
                validation_errors['db_collection'] = ['If is_field_custom is selected , db_collection is required.']
            if data_dict.get('is_field_custom') and 'db_field_reference' in data_keys and data_dict.get('db_field_reference') and 'db_collection' in data_keys and data_dict.get('db_collection'):
                if (data_dict.get('db_collection') == "RECORDS" and data_dict.get('db_field_reference') not in [f.name for f in Record._meta.get_fields()]) or (data_dict.get('db_collection') == "GROUPS" and data_dict.get('db_field_reference') not in [f.name for f in Group._meta.get_fields()]) or (data_dict.get('db_collection') == "USERS" and data_dict.get('db_field_reference') not in [f.name for f in User._meta.get_fields()]):
                    validation_errors['db_field_reference'] = ['Field name is invalid.']
            if data_dict.get('default_value') is not None and len(str(data_dict.get('default_value')).strip()) > 0:
                print('tenho de correr validações para todos os campos como está no validation_helper run_validations') 


            if validation_errors:
                raise ValidationError(validation_errors)
            return data
        class Meta:
            fields = ['name', 'optional', 'options', 'field_type', 'placeholder','format','label']
   
    validations = serializers.DictField(allow_empty=True, child = ValidationsSerializer())
    send_type = serializers.ChoiceField(choices = SEND_TYPE_CHOICES)
    send_email_to = serializers.ListField(required = False,allow_null = True,allow_empty=True, child = serializers.EmailField())
    send_email_to_cc = serializers.ListField(required = False,allow_null = True,allow_empty=True, child = serializers.EmailField())
    send_email_to_bcc = serializers.ListField(required = False,allow_null = True,allow_empty=True, child = serializers.EmailField())


    def validate(self,data):
        data_dict = dict(data)
        data_keys = data.keys()
        send_type = data_dict.get('send_type')
        validation_errors = {}
        if send_type in ["EMAIL","DOCUMENT_EMAIL"] and ('send_email_to' not in data_keys or ('send_email_to' in data_keys and (data_dict.get('send_email_to') == [] or data_dict.get('send_email_to') == None))):
            validation_errors['send_email_to'] = ['When send_type is EMAIL or DOCUMENT_EMAIL, the field send_email_to is required.']
        if send_type in ["DOCUMENT","DOCUMENT_EMAIL"] and ('file' not in data_keys or ('file' in data_keys and (data_dict.get('file') == "" or data_dict.get('file') == None))):
            validation_errors['file'] = ['When send_type is DOCUMENT or DOCUMENT_EMAIL, the field file is required.']

        if validation_errors:
            raise ValidationError(validation_errors)
        return data
        
    class Meta:
        model = TemplateLogic
        fields = ['title','file','group','slug','validations','send_type','send_email_to','send_email_to_cc','send_email_to_bcc']
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




