from rest_framework import serializers
from records.models import Record
from rest_framework.validators import UniqueValidator
from rest_framework import serializers


GENDER_CHOICES = (
    ("WOMAN",'Woman'),
    ("MALE",'Man'),
    ("OTHER",'Other')
)

MARITAL_STATUS_CHOICES = (
    ("SINGLE",'Single'),
    ("MARIED",'Maried'),
    ("DIVORCED",'Divorced'),
    ("WIDOWER",'Widower')
)

STATUS_CHOICES = (
    ("INACTIVE",'Inactive'),
    ("ACTIVE",'Active'),
    ("PENDING",'Pending'),
    ("COMPLETED",'Completed'),
    ("ARCHIVED",'Archived')
)

class RecordCreateSerializer(serializers.ModelSerializer):

    gender = serializers.ChoiceField(choices = GENDER_CHOICES)
    spouse_gender = serializers.ChoiceField(choices = GENDER_CHOICES, allow_null = True)
    marital_status = serializers.ChoiceField(choices = MARITAL_STATUS_CHOICES)
    status = serializers.ChoiceField(choices = STATUS_CHOICES)
    class Meta:
        model = Record
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {
                'validators': [
                    UniqueValidator(
                        queryset=Record.objects.all(),
                        message= "Name must be unique"
                    )
                ]
            }
        }


class RecordUpdateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required = False)
    name = serializers.CharField(required = False)
    gender = serializers.ChoiceField(choices = GENDER_CHOICES, required = False)
    spouse_gender = serializers.ChoiceField(choices = GENDER_CHOICES, required = False)
    marital_status = serializers.ChoiceField(choices = MARITAL_STATUS_CHOICES, required = False)
    status = serializers.ChoiceField(choices = STATUS_CHOICES, required = False)
    class Meta:
        model = Record
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {
                'validators': [
                    UniqueValidator(
                        queryset=Record.objects.all(),
                        message= "Name must be unique"
                    )
                ]
            }
        }
       
    
    
        
        
        