from django.forms import ValidationError
from rest_framework import serializers
from accounts.models import User
from groups.models import Group
from records.models import Record
from template_logic.models import TemplateLogic

from template_logic.validation_helper import run_template_validations

import logging
logger = logging.getLogger(__name__)

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
        class StringListField(serializers.ListField):
            child = serializers.CharField()

        class CharOrListField(serializers.ListField):
            child = serializers.CharField()

            def to_internal_value(self, data):
                if isinstance(data,list):
                    return super().to_internal_value(data)
                else:
                    return [data]
                
            def to_representation(self, value):
                if isinstance(value,list):
                    return super().to_representation(value)
                else:
                    return value

        name = serializers.CharField(error_messages = {
            "required": "Este campo é obrigatório",
        })
        optional = serializers.BooleanField(default=True)
        options = StringListField(required=False, allow_empty=True, allow_null=True)
        field_type = serializers.ChoiceField(choices = FIELD_TYPE_CHOICES, error_messages = {
            "required": "Este campo é obrigatório",
            "invalid_choice": "Opção inválida"
        })
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
        default_value = CharOrListField(required=False,allow_null= True, allow_empty= True, child=serializers.CharField())

        def validate(self, data):
            data_dict = dict(data)
            data_keys = data.keys()
            field_type= data_dict.get('field_type')
            is_field_custom= data_dict.get('is_field_custom')
            validation_errors = {}
            if field_type in ["DATE","DATETIME","TIME"] and ('format' not in data_keys or data_dict.get('format') == ""):
                validation_errors['format'] = ['O campo formato da data é obrigatório.']
            if field_type in ["DATE","DATETIME","TIME"] and ('is_date_numeric' not in data_keys or data_dict.get('is_date_numeric') == ""):
                validation_errors['is_date_numeric'] = ['O campo data por extenso é obrigatório.']
            # if field_type in ["DATE"] and data_dict.get('format') not in ["DAY_MONTH_YEAR","MONTH_YEAR","DAY_MONTH"]:
            #     validation_errors['format'] = ['Apenas são válidas as opções Dia/Mês/Ano, Mês/Ano ou Dia/Mês.']
            # if field_type in ["TIME"] and data_dict.get('format') not in ["HOURS_ONLY","MINUTES_ONLY","SECONDS_ONLY","HOURS_MINUTES_SECONDS","HOURS_MINUTES","MINUTES_SECONDS"]:
            #     validation_errors['format'] = ['When field_type is TIME, format can be HOURS_ONLY, MINUTES_ONLY, SECONDS_ONLY, HOURS_MINUTES_SECONDS, HOURS_MINUTES or MINUTES_SECONDS.']
            # if field_type in ["DATETIME"] and data_dict.get('format') not in ["DAY_MONTH_YEAR_HOUR_MINUTE_SECOND","DAY_MONTH_YEAR_HOUR_MINUTE","DAY_MONTH_YEAR_HOUR","DAY_MONTH_HOUR_MINUTE_SECOND","DAY_MONTH_HOUR_MINUTE","DAY_MONTH_HOUR","MONTH_YEAR_HOUR_MINUTE_SECOND","MONTH_YEAR_HOUR_MINUTE","MONTH_YEAR_HOUR"]:
            #     validation_errors['format'] = ['When field_type is DATETIME, format can be DAY_MONTH_YEAR_HOUR_MINUTE_SECOND, DAY_MONTH_YEAR_HOUR_MINUTE, DAY_MONTH_YEAR_HOUR, DAY_MONTH_HOUR_MINUTE_SECOND, DAY_MONTH_HOUR_MINUTE, DAY_MONTH_HOUR, MONTH_YEAR_HOUR_MINUTE_SECOND, MONTH_YEAR_HOUR_MINUTE, MONTH_YEAR_HOUR.']
            if field_type in ["SELECT","MULTISELECT", "RADIO"] and ('options' not in data_keys or len(data_dict.get('options')) == 0):
                validation_errors['options'] = ['O campo "Opções" é obrigatório.']
            if field_type in ["SELECT","MULTISELECT", "RADIO"] and data_dict.get('optional') and ('min' not in data_keys or data_dict.get('min') == 0):
                validation_errors['min'] = ['O campo "mínimo" é obrigatório.']
            if not is_field_custom and ('db_field_reference' not in data_keys or data_dict.get('db_field_reference') == ""):
                validation_errors['db_field_reference'] = ['o campo "Campo da Tabela" é obrigatório.']
            if not is_field_custom and ('db_collection' not in data_keys or data_dict.get('db_collection') == ""):
                validation_errors['db_collection'] = ['O campo "Tabela" é obrigatório.']
            if data_dict.get('is_field_custom') and 'db_field_reference' in data_keys and data_dict.get('db_field_reference') and 'db_collection' in data_keys and data_dict.get('db_collection'):
                if (data_dict.get('db_collection') == "RECORDS" and data_dict.get('db_field_reference') not in [f.name for f in Record._meta.get_fields()]) or (data_dict.get('db_collection') == "GROUPS" and data_dict.get('db_field_reference') not in [f.name for f in Group._meta.get_fields()]) or (data_dict.get('db_collection') == "USERS" and data_dict.get('db_field_reference') not in [f.name for f in User._meta.get_fields()]):
                    validation_errors['db_field_reference'] = ['O campo "Nome do campo" é obrigatório.']
            if data_dict.get('default_value') is not None and len(str(data_dict.get('default_value')).strip()) > 0:                 
                prep_var_validation = [{"validations" : {"default_value":data}}]      
                result = run_template_validations(prep_var_validation,{'default_value' : data.get('default_value')}, "CREATE_TEAMPLATE")
                if 'errors' in result and result.get('errors') is not None:
                    errors = result.get('errors')
                    if 'default_value' in errors:
                        if type(errors.get('default_value')) is dict:
                            default_value_errors = errors.get('default_value')
                            for key,value in default_value_errors.items():
                                if 'default_value' not in validation_errors:
                                    validation_errors['default_value'] = []
                                validation_errors['default_value'].append(value) 
                        else:
                            validation_errors['default_value'] = errors.get('default_value')   
            if validation_errors:
                raise ValidationError(validation_errors)
            return data
        class Meta:
            fields = ['name', 'optional', 'options', 'field_type', 'placeholder','format','label']
    title = serializers.CharField(required = True, max_length = 256, error_messages = {
        "required": "Este campo é obrigatório"
    })
    group = serializers.PrimaryKeyRelatedField(required = True, queryset = Group.objects.all(), error_messages = {
        "required": "Este campo é obrigatório"
    })
    validations = serializers.ListField(allow_empty=True, child = ValidationsSerializer())
    send_type = serializers.ChoiceField(choices = SEND_TYPE_CHOICES, error_messages = {
        "required": "Este campo é obrigatório",
        "invalid_choice": "Opção inválida"
    })
    send_email_to = serializers.ListField(required = False,allow_null = True,allow_empty=True, child = serializers.EmailField())
    send_email_to_cc = serializers.ListField(required = False,allow_null = True,allow_empty=True, child = serializers.EmailField())
    send_email_to_bcc = serializers.ListField(required = False,allow_null = True,allow_empty=True, child = serializers.EmailField())
    file = serializers.CharField(required = False,allow_null = True, max_length = 100000)

    def validate(self,data):
        data_dict = dict(data)
        data_keys = data.keys()
        send_type = data_dict.get('send_type')
        title = data_dict.get('title')
        validation_errors = {}
        if title is None or title == "":
            validation_errors['title'] = ['O campo "Título" é obrigatório.'] 
        if title is not None and len(str(title).strip()) > 0 and TemplateLogic.objects.filter(title = title, group = data_dict.get('group')).exists():
            validation_errors['title'] = ['O Título tem de ser único.']
        if send_type in ["EMAIL","DOCUMENT_EMAIL"] and ('send_email_to' not in data_keys or ('send_email_to' in data_keys and (data_dict.get('send_email_to') == [] or data_dict.get('send_email_to') == None))):
            validation_errors['send_email_to'] = ['O campo "Enviar email para" é obrigatório.']
        if send_type in ["DOCUMENT","DOCUMENT_EMAIL"] and ('file' not in data_keys or ('file' in data_keys and (data_dict.get('file') == "" or data_dict.get('file') == None))):
            validation_errors['file'] = ['O campo "Ficheiro" é obrigatório.']

        if validation_errors:
            raise ValidationError(validation_errors)
        return data
        
  
    class Meta:
        model = TemplateLogic
        fields = ['title','file','group','validations','send_type','send_email_to','send_email_to_cc','send_email_to_bcc']
        


class EditUploadSerializer(serializers.ModelSerializer):    
    class ValidationsSerializer(serializers.Serializer):
        class StringListField(serializers.ListField):
            child = serializers.CharField()
        class CharOrListField(serializers.ListField):
            child = serializers.CharField()

            def to_internal_value(self, data):
                if isinstance(data,list):
                    return super().to_internal_value(data)
                else:
                    return [data]
                
            def to_representation(self, value):
                if isinstance(value,list):
                    return super().to_representation(value)
                else:
                    return value

        name = serializers.CharField(error_messages = {
            "required": "Este campo é obrigatório",
        })
        optional = serializers.BooleanField(default=True)
        options = StringListField(required=False, allow_empty=True, allow_null=True)
        field_type = serializers.ChoiceField(choices = FIELD_TYPE_CHOICES, required = True, error_messages = {
            "required": "Este campo é obrigatório",
            "invalid_choice": "Opção inválida"
        })
        placeholder = serializers.CharField(required = False)
        format = serializers.ChoiceField(required=False,allow_null = True, allow_blank = True,choices = FORMAT_CHOICES)
        #is_date_numerica true = escrever por extenso
        is_date_numeric = serializers.BooleanField(allow_null = True, required=False)
        label = serializers.CharField(required = False,allow_blank=True)
        is_field_custom = serializers.BooleanField()
        db_collection = serializers.ChoiceField(choices = DB_COLLECTION_CHOICES, allow_null=True, required = False)
        db_field_reference = serializers.CharField(required = False,allow_blank=True)
        min = serializers.IntegerField(required = False, allow_null = True)
        max = serializers.IntegerField(required = False, allow_null = True)
        default_value = CharOrListField(required=False,allow_null= True, allow_empty= True, child=serializers.CharField())

        def validate(self, data):
            data_dict = dict(data)
            data_keys = data.keys()
            validation_errors = {}
            if not data_dict.get('field_type'):
                validation_errors['field_type'] = ['Field is required.']
            if data_dict.get('is_field_custom') is None:
                validation_errors['is_field_custom'] = ['Field is required.']
            if data_dict.get('optional') is None:
                validation_errors['optional'] = ['Field is required.']
            if not data_dict.get('name') or data_dict.get('name') == "":
                validation_errors['name'] = ['Field is required.']
            field_type= data_dict.get('field_type')
            is_field_custom= data_dict.get('is_field_custom')
            
            if field_type in ["DATE","DATETIME","TIME"] and ('format' not in data_keys or data_dict.get('format') == ""):
                validation_errors['format'] = ['When field_type is DATE, DATETIME or TIME, the field format is required.']
            if field_type in ["DATE","DATETIME","TIME"] and ('is_date_numeric' not in data_keys or data_dict.get('is_date_numeric') == ""):
                validation_errors['is_date_numeric'] = ['When field_type is DATE, DATETIME or TIME, the field is_date_numeric is required.']
            # if field_type in ["DATE"] and data_dict.get('format') not in ["DAY_MONTH_YEAR","MONTH_YEAR","DAY_MONTH"]:
            #     validation_errors['format'] = ['When field_type is DATE, format can be DAY_MONTH_YEAR, MONTH_YEAR or DAY_MONTH.']
            # if field_type in ["TIME"] and data_dict.get('format') not in ["HOURS_ONLY","MINUTES_ONLY","SECONDS_ONLY","HOURS_MINUTES_SECONDS","HOURS_MINUTES","MINUTES_SECONDS"]:
            #     validation_errors['format'] = ['When field_type is TIME, format can be HOURS_ONLY, MINUTES_ONLY, SECONDS_ONLY, HOURS_MINUTES_SECONDS, HOURS_MINUTES or MINUTES_SECONDS.']
            # if field_type in ["DATETIME"] and data_dict.get('format') not in ["DAY_MONTH_YEAR_HOUR_MINUTE_SECOND","DAY_MONTH_YEAR_HOUR_MINUTE","DAY_MONTH_YEAR_HOUR","DAY_MONTH_HOUR_MINUTE_SECOND","DAY_MONTH_HOUR_MINUTE","DAY_MONTH_HOUR","MONTH_YEAR_HOUR_MINUTE_SECOND","MONTH_YEAR_HOUR_MINUTE","MONTH_YEAR_HOUR"]:
            #     validation_errors['format'] = ['When field_type is DATETIME, format can be DAY_MONTH_YEAR_HOUR_MINUTE_SECOND, DAY_MONTH_YEAR_HOUR_MINUTE, DAY_MONTH_YEAR_HOUR, DAY_MONTH_HOUR_MINUTE_SECOND, DAY_MONTH_HOUR_MINUTE, DAY_MONTH_HOUR, MONTH_YEAR_HOUR_MINUTE_SECOND, MONTH_YEAR_HOUR_MINUTE, MONTH_YEAR_HOUR.']
            if field_type in ["SELECT","MULTISELECT", "RADIO"] and ('options' not in data_keys or data_dict.get('options') is None):
                validation_errors['options'] = ['O campo "Opções" é obrigatório.']
            if field_type in ["SELECT","MULTISELECT", "RADIO"] and data_dict.get('optional') and ('min' not in data_keys or data_dict.get('min') == 0):
                validation_errors['min'] = ['Quando o campo é de opções, multiplas opções o campo "Minimo" não pode ser 0']
            if not is_field_custom and ('db_field_reference' not in data_keys or data_dict.get('db_field_reference') == ""):
                validation_errors['db_field_reference'] = ['o campo "Campo da Tabela" é obrigatório.']
            if not is_field_custom and ('db_collection' not in data_keys or data_dict.get('db_collection') == ""):
                validation_errors['db_collection'] = ['O campo "Tabela" é obrigatório.']
            if data_dict.get('is_field_custom') and 'db_field_reference' in data_keys and data_dict.get('db_field_reference') and 'db_collection' in data_keys and data_dict.get('db_collection'):
                if (data_dict.get('db_collection') == "RECORDS" and data_dict.get('db_field_reference') not in [f.name for f in Record._meta.get_fields()]) or (data_dict.get('db_collection') == "GROUPS" and data_dict.get('db_field_reference') not in [f.name for f in Group._meta.get_fields()]) or (data_dict.get('db_collection') == "USERS" and data_dict.get('db_field_reference') not in [f.name for f in User._meta.get_fields()]):
                    validation_errors['db_field_reference'] = ['O campo "Nome do campo" é inválido.']
            if data_dict.get('default_value') is not None and len(str(data_dict.get('default_value')).strip()) > 0:                 
                prep_var_validation = [{"validations" : {"default_value":data}}]           
                result = run_template_validations(prep_var_validation,{'default_value' : data.get('default_value')}, "CREATE_TEAMPLATE")
                if 'errors' in result and result.get('errors') is not None:
                    errors = result.get('errors')
                    if 'default_value' in errors:
                        if type(errors.get('default_value')) is dict:
                            default_value_errors = errors.get('default_value')
                            for key,value in default_value_errors.items():
                                if 'default_value' not in validation_errors:
                                    validation_errors['default_value'] = []
                                validation_errors['default_value'].append(value) 
                        else:
                            validation_errors['default_value'] = errors.get('default_value')   
            if validation_errors:
                raise ValidationError(validation_errors)
            return data
        class Meta:
            fields = ['name', 'optional', 'options', 'field_type', 'placeholder','format','label']
    title = serializers.CharField(required = False,allow_null = True, max_length = 256, error_messages = {
        "required": "Este campo é obrigatório"
    })
    group = serializers.PrimaryKeyRelatedField(required = False, allow_null = True, queryset = Group.objects.all(), error_messages = {
        "required": "Este campo é obrigatório"
    })
    validations = serializers.ListField(allow_empty=True, child = ValidationsSerializer())
    send_type = serializers.ChoiceField(choices = SEND_TYPE_CHOICES, allow_null = True, error_messages = {
        "required": "Este campo é obrigatório",
        "invalid_choice": "Opção inválida"
    })
    send_email_to = serializers.ListField(required = False,allow_null = True,allow_empty=True, child = serializers.EmailField())
    send_email_to_cc = serializers.ListField(required = False,allow_null = True,allow_empty=True, child = serializers.EmailField())
    send_email_to_bcc = serializers.ListField(required = False,allow_null = True,allow_empty=True, child = serializers.EmailField())
    file = serializers.CharField(required = False,allow_null = True, max_length = 100000)

    def validate(self,data):
        data_dict = dict(data)
        data_keys = data.keys()
        send_type = data_dict.get('send_type') if data_dict.get('send_type') else self.instance.send_type
        send_email_to = data_dict.get('send_email_to') if data_dict.get('send_email_to') else self.instance.send_email_to
        validation_errors = {}
        title = data_dict.get('title')
        if title is None or title == "":
            validation_errors['title'] = ['O campo "Título" é obrigatório.'] 
        if title is not None and len(str(title).strip()) > 0 and TemplateLogic.objects.filter(title = title, group = data_dict.get('group')).exclude(id = self.instance.id).exists():
            validation_errors['title'] = ['O Título tem de ser único.']
        if send_type in ["EMAIL","DOCUMENT_EMAIL"] and (send_email_to == [] or send_email_to == None):
            validation_errors['send_email_to'] = ['When send_type is EMAIL or DOCUMENT_EMAIL, the field send_email_to is required.']
        if send_type in ["DOCUMENT","DOCUMENT_EMAIL"] and ('file' not in data_keys or ('file' in data_keys and (data_dict.get('file') == "" or data_dict.get('file') == None))):
            validation_errors['file'] = ['When send_type is DOCUMENT or DOCUMENT_EMAIL, the field file is required.']

        if validation_errors:
            raise ValidationError(validation_errors)
        return data
        
    class Meta:
        model = TemplateLogic
        fields = ['title','file','group','validations','send_type','send_email_to','send_email_to_cc','send_email_to_bcc']




