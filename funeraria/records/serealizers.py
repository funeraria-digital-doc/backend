from django.forms import CharField
from rest_framework import serializers
from accounts.serealizers import UserSerializer
from records.models import Record
from rest_framework.validators import UniqueValidator
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers

class RecordSerializer(serializers.ModelSerializer):
    # group_user = UserSerializer(many=True)
    class Meta:
        model = Record
        fields = '__all__'

class RecordCreateSerializer(serializers.ModelSerializer):
#     created_by
# updated_by
# created_at
# updated_at
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
    class Meta:
        model = Record
        fields = '__all__'
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
       
    
    
        
        
        