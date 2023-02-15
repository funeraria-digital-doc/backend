from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

from accounts.serealizers import RegistrationSerializer,EditProfileSerializer
from accounts.models import User
from rest_framework.authtoken.models import Token

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.decorators import parser_classes

from funeraria.permissions import IsAdmin, IsSuperUser, isEqualOrUpperPermission

@swagger_auto_schema(       
    method='post',
    operation_description="Login user",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties= {
            'username': openapi.Schema(title="username",type=openapi.TYPE_STRING),
            'password': openapi.Schema(title="password",type=openapi.TYPE_STRING),
        },
    ),
)
@api_view(['POST'])
def login(request):
    username = request.data['username']
    password = request.data['password']
    if username and password:
        # Try to authenticate the user using Django auth framework.
        user = authenticate(request=request, username=username, password=password)
        if not user:
            # If we don't have a regular user, raise a ValidationError
            return Response('Access denied: wrong email or password.',status=status.HTTP_200_OK)
        else:
            token = Token.objects.get_or_create(user=user)
            if token is not None and token[0] is not None:
                data = {
                    'name': user.username,
                    'email': user.email,
                    'token' : str(token[0]),
                    'user_permissions': user.get_user_permissions(),
                    'group_permissions': user.get_group_permissions()
                }
                return Response(data,status=status.HTTP_200_OK) 
            else :
                return Response('error creating token',status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    else:
        return Response('Both "username" and "password" are required.',status=status.HTTP_200_OK)

@swagger_auto_schema(       
    method='post',
    operation_description="Logout a user"
)    
@api_view(['POST'])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)

@swagger_auto_schema(       
    method='post',
    operation_description="Register a user",
    request_body=RegistrationSerializer
)
@api_view(['POST'])
def registration(request):
    serializer = RegistrationSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        account = serializer.save()
        
        data['response'] = "Registration Successful!"
        data['username'] = account.username
        data['email'] = account.email

        token = Token.objects.get(user=account).key
        data['token'] = token       
    else:
        data = serializer.errors
    
    return Response(data, status=status.HTTP_201_CREATED)

@swagger_auto_schema(       
    method='get',
    operation_description="Get user profile information"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request): 
    user = Token.objects.get(key=request.auth.key).user
    if(User.objects.filter(username=user.username).exists()):
        data = {
            'name': user.username,
            'email': user.email,
            'user_permissions': user.get_user_permissions(),
            'group_permissions': user.get_group_permissions()
        }
        return Response(data, status=status.HTTP_200_OK)
    return Response("User does not exist", status=status.HTTP_406_NOT_ACCEPTABLE)

@swagger_auto_schema(
    method='patch',
    request_body=EditProfileSerializer,
    operation_description="Edit a User profile"
)    
@api_view(['PATCH'])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def edit_profile(request, *args, **kwargs):

    print(request.auth)
    user = Token.objects.get(key=request.auth).user
    if(User.objects.filter(username=user.username).exists()):
        print(user)
        serializer = EditProfileSerializer(data = request.data, partial=True)   
        print(serializer.is_valid())
        if serializer.is_valid():
            try:            
                serializer.update(instance = user, validated_data=serializer.validated_data)
                return Response(serializer.data, status = status.HTTP_200_OK)
            except:
                return Response(
                    {
                        'error' : "something went wrong updating user",
                        "data" : serializer.errors
                    }, 
                    status = status.HTTP_404_NOT_FOUND
                )
        else:
            return Response({'error' : serializer.errors}, status = status.HTTP_400_BAD_REQUEST) 
    return Response({'error' : "User not found"}, status = status.HTTP_404_NOT_FOUND) 

@swagger_auto_schema(
    method='post',
    request_body=RegistrationSerializer,
    operation_description="Create a super user"
)    
@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsSuperUser])
def create_superuser(request, *args, **kwargs):
    serializer = RegistrationSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        user = User.objects.create_superuser(
            serializer.validated_data['username'], 
            serializer.validated_data['email'], 
            serializer.validated_data['password']
        )
        
        data['response'] = "Registration Successful!"
        data['username'] = user.username
        data['email'] = user.email  
        data['is_superuser'] = user.is_superuser  
    else:
        data = serializer.errors
    
    return Response(data, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='post',
    request_body=RegistrationSerializer,
    operation_description="Create a staff user"
)    
@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsAdmin])
def create_staffuser(request, *args, **kwargs): 
    serializer = RegistrationSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        user = User.objects.create_user(serializer.validated_data['username'], serializer.validated_data['email'], serializer.validated_data['password'])  
        user.is_staff=True 
        user.save()
        data['response'] = "Registration Successful!"
        data['username'] = user.username
        data['email'] = user.email  
        data['is_superuser'] = user.is_superuser  
        data['is_staff'] = user.is_staff  
    else:
        data = serializer.errors
    
    return Response(data, status=status.HTTP_201_CREATED)

@swagger_auto_schema(       
    method='get',
    operation_description="Get user profile information"
)
@api_view(['GET'])
@permission_classes([isEqualOrUpperPermission])
def profile_admin(request, *args, **kwargs): 
    user = User.objects.filter(id=kwargs['pk']).first()
    if user is not None:
        data = {
            'user': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'user_permissions': user.get_user_permissions(),
            'group_permissions': user.get_group_permissions()
        }
        return Response(data, status=status.HTTP_200_OK)
    return Response("User does not exist", status=status.HTTP_406_NOT_ACCEPTABLE)

@swagger_auto_schema(
    method='patch',
    request_body=EditProfileSerializer,
    operation_description="Edit a User profile"
)    
@api_view(['PATCH'])
@parser_classes([MultiPartParser])
@permission_classes([isEqualOrUpperPermission])
def edit_profile_admin(request, *args, **kwargs):
    user = User.objects.filter(id=kwargs['pk']).first()
    if user is not None:
        serializer = EditProfileSerializer(data = request.data, partial=True)   
        if serializer.is_valid():
            try:            
                serializer.update(instance = user, validated_data=serializer.validated_data)
                return Response(serializer.data, status = status.HTTP_200_OK)
            except:
                return Response({'error' : "something went wrong updating user","data" : serializer.errors}, status = status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error' : serializer.errors}, status = status.HTTP_400_BAD_REQUEST) 
    return Response({'error' : "User not found"}, status = status.HTTP_404_NOT_FOUND) 

@swagger_auto_schema(
    method='delete',
    operation_description="Delete a user"
) 
@api_view(['DELETE'])
@permission_classes([IsAdmin])
def remove(request, *args, **kwargs):
    user = User.objects.filter(id=kwargs.get('pk')).first()
    if user is None:
        return Response({"error" : "User does not exist!"},status=status.HTTP_404_NOT_FOUND)
    user.delete()
    return Response({"success" : "User deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)    
    
