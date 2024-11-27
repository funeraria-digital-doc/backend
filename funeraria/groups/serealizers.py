from rest_framework import serializers
from accounts.serealizers import UserSerializer
from groups.models import Group
from rest_framework.validators import UniqueValidator
from rest_framework import serializers

class GroupSerializer(serializers.ModelSerializer):
    group_user = UserSerializer(many=True)
    page = serializers.JSONField(allow_null = True, required= False)
    class Meta:
        model = Group
        fields = ['id','name', 'page', 'slug','user']

class GroupCreateSerializer(serializers.ModelSerializer):
    page = serializers.JSONField(allow_null = True, required= False)
    class Meta:
        model = Group
        fields = ['id', 'name', 'page', 'slug']
        extra_kwargs = {
            'user': {'read_only': True},
            'name': {
                'validators': [
                    UniqueValidator(
                        queryset=Group.objects.all(),
                        message="Name must be unique"
                    )
                ]
            }
        }


class GroupUpdateSerializer(serializers.ModelSerializer):
    page = serializers.JSONField(allow_null = True, required= False)
    class Meta:
        model = Group
        fields = ['id', 'name', 'page', 'slug']
        extra_kwargs = {
            'user': {'read_only': True},
            'name': {
                'validators': [
                    UniqueValidator(
                        queryset=Group.objects.all(),
                        message="Name must be unique"
                    )
                ]
            }
        }
       
    
    
        
        
        