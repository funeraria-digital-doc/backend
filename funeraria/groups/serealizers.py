from django.forms import CharField
from rest_framework import serializers
from accounts.serealizers import UserSerializer
from groups.models import Group
from rest_framework.validators import UniqueValidator
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers

class GroupSerializer(serializers.ModelSerializer):
    group_user = UserSerializer(many=True)
    class Meta:
        model = Group
        fields = ['id','name','user']

class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']
        extra_kwargs = {
            'user' : {'read_only': True},
            'name': {
                'validators': [
                    UniqueValidator(
                        queryset=Group.objects.all(),
                        message= "Name must be unique"
                    )
                ]
            }
        }


class GroupUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id','name']
        extra_kwargs = {
            'user' : {'read_only': True},
            'name': {
                'validators': [
                    UniqueValidator(
                        queryset=Group.objects.all(),
                        message= "Name must be unique"
                    )
                ]
            }
        }
       
    
    
        
        
        