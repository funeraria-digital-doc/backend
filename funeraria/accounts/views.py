from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

from accounts.serealizers import RegistrationSerializer
from accounts.models import User
from rest_framework.authtoken.models import Token

@api_view(['POST'])
def login(request):
    username = request.data['username']
    password = request.data['password']
    if username and password:
        # Try to authenticate the user using Django auth framework.
        user = authenticate(request=request, username=username, password=password)
        if not user:
            # If we don't have a regular user, raise a ValidationError
            return Response('Access denied: wrong username or password.',status=status.HTTP_200_OK)
        else:
            token = Token.objects.get(user=user).key
            data = {
                'name': user.username,
                'email': user.email,
                'token' : token,
                'user_permissions': user.get_user_permissions(),
                'group_permissions': user.get_group_permissions()
            }
            return Response(data,status=status.HTTP_200_OK)       
    else:
        return Response('Both "username" and "password" are required.',status=status.HTTP_200_OK)
    
    

@api_view(['POST'])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)


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

    
    
    
