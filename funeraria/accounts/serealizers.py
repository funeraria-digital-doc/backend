
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from accounts.models import User
from groups.models import Group
import logging
logger = logging.getLogger(__name__)
class RegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['username', 'email' ,'password', 'password_confirm']
        extra_kwargs = {
            'password' : {'write_only': True}
        }
    
    def save(self):

        password = self.validated_data['password']
        password_confirm = self.validated_data['password_confirm']

        if password != password_confirm:
            raise serializers.ValidationError({'error': 'P1 and P2 should be same!'})

        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'error': 'Email already exists!'})

        account = User(email=self.validated_data['email'], username=self.validated_data['username'])
        account.set_password(password)
        account.save()

        return account

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email']
        extra_kwargs = {
            'password' : {'write_only': True}
        }

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password']



class EditProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False,validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(required=False,validators=[UniqueValidator(queryset=User.objects.all())])
    class Meta:
        model = User
        fields = ['username', 'email']

class EditProfileAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False,validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(required=False,validators=[UniqueValidator(queryset=User.objects.all())])
    class Meta:
        model = User
        fields = '__all__'

class ProfilePictureUploadSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(required=True, allow_empty_file=False)

    def validate_file(self, value):
        max_size = 5 * 1024 * 1024  # Maximum size in bytes (e.g., 5MB)
        if value.size > max_size:
            raise serializers.ValidationError("Picture size should not exceed 5MB.")
        allowed_types = ['image/jpeg', 'image/png']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only JPEG and PNG image formats are allowed.")

        return value
        
    class Meta:
        model = User
        fields = ['file']


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    status = serializers.ChoiceField(required=False, choices=User.Status.choices, default=User.Status.ACTIVE)
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)
    group_user = serializers.PrimaryKeyRelatedField(required = False, allow_null = True , queryset = Group.objects.all()) 
    class Meta:
        model = User
        fields = ['username', 'email', 'status', 'is_staff', 'is_superuser', 'group_user']

class EditUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    status = serializers.ChoiceField(required=False, choices=User.Status.choices)
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)
    group_user = serializers.PrimaryKeyRelatedField(required = False, allow_null = True , queryset = Group.objects.all()) 
    class Meta:
        model = User
        fields = ('id','username', 'email', 'status', 'is_staff', 'is_superuser', 'group_user')
        #read_only_fields = ['id']
    def validate(self, data):
        data_dict = dict(data)
        data_keys = data.keys()
        logger.info(data_dict)
        logger.info(data_keys)
        request = self.instance
        logger.info(request)
        if 'username' in data_keys:
            logger.info(data_dict['username'])
        return data
    

        
        
    
    