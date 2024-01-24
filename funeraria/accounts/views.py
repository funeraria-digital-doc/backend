from rest_framework.decorators import api_view, permission_classes
#,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from accounts.serealizers import EditProfileSerializer, ProfilePictureUploadSerializer, CreateUserSerializer, EditUserSerializer
from accounts.models import User
#from rest_framework.authtoken.models import Token
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
#from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
#from rest_framework.decorators import parser_classes
from funeraria.permissions import  IsAdminOrUpper
#, IsSuperUser, isEqualOrUpperPermission,IsAdmin
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import F
from django.contrib.auth.models import update_last_login
import logging
logger = logging.getLogger(__name__)


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
        user = authenticate(username=username, password=password)
        if not user:
            return Response('Acesso negado. Nome ou palavra-passe erradas.',status=status.HTTP_401_UNAUTHORIZED)
        else:
            refresh = RefreshToken.for_user(user)
            refresh['name']= user.username
            refresh['email']= user.email
            refresh['role']= getRole(user)
            update_last_login(None, user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            },status=status.HTTP_200_OK)
    else:
        return Response('Nome ou palavra-passe são obrigatórios.',status=status.HTTP_200_OK)
    
@swagger_auto_schema(       
    method='post',
    operation_description="Change user Password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties= {
            'password': openapi.Schema(title="password",type=openapi.TYPE_STRING),
            'confirm_password': openapi.Schema(title="confirm_password",type=openapi.TYPE_STRING),
        },
    ),
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    password = request.data['password']
    confirm_password = request.data['confirm_password']
    if(not confirm_password or not password) :
        return Response('A palavra-passe e a sua confirmação são obrigatórios.',status=status.HTTP_400_BAD_REQUEST)
    
    if (confirm_password != password):
        return Response('A palavra-passe e a sua confirmação devem ser iguais.',status=status.HTTP_400_BAD_REQUEST)
    
    # Try to authenticate the user using Django auth framework.
    user = User.objects.get(id=request.user.id)
    logger.info(user)
    if not user:
        # If we don't have a regular user, raise a ValidationError
        return Response('Nenhum utilizador associado.',status=status.HTTP_401_UNAUTHORIZED)
    else:
        user.set_password(password)
        try:
            user.save()
            return Response({'success': True},status=status.HTTP_200_OK) 
        except Exception as e:
            logger.info(e)
            return Response('Erro a alterar a palavra-passe',status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
            

@swagger_auto_schema(       
    method='post',
    operation_description="File Upload",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties= {
            'file': openapi.Schema(title="file",type=openapi.TYPE_FILE)
        },
    ),
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def file_upload(request):
    data = {}
    data['file'] = request.data['file']
    user = request.user
    if not user:
        return Response('Nenhum utilizador associado.',status=status.HTTP_401_UNAUTHORIZED)
    serializer = ProfilePictureUploadSerializer(data = data,instance=user, partial=True)   
    if serializer.is_valid():
        try:
            serializer.update(instance = user, validated_data=serializer.validated_data)
            return Response({'success': True},status=status.HTTP_200_OK) 
        except Exception as e:
            return Response('Erro ao carregar a imagem de perfil',status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    else:
        return Response({'error' : serializer.errors},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
 

@swagger_auto_schema(       
    method='post',
    operation_description="Logout a user"
)    
@api_view(['POST'])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)

@swagger_auto_schema(       
    method='get',
    operation_description="Get user profile information"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request): 
    user = {
        'id' : request.user.id,
        'name' : request.user.username,
        'email' : request.user.email,
        'role' : getRole(request.user)
    }
    if user: 
        return Response(user, status=status.HTTP_200_OK)
    return Response("Utilizador não existe", status=status.HTTP_406_NOT_ACCEPTABLE)

@swagger_auto_schema(       
    method='get',
    operation_description="Get user profile image"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_image(request): 
    if not request.user:
        return Response("Utilizador não existe", status=status.HTTP_406_NOT_ACCEPTABLE)
    
    user_data = {
        'image' : User.objects.get(id=request.user.id).__getattribute__('file')
    }
    return Response(user_data, status=status.HTTP_200_OK)
    
@swagger_auto_schema(
    method='patch',
    request_body=EditProfileSerializer,
    operation_description="Edit a User profile"
)    
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_profile(request, *args, **kwargs):
    if request.user:
        serializer = EditProfileSerializer(data = request.data,instance=request.user, partial=True)   
        if serializer.is_valid():
            try:            
                serializer.update(instance = request.user, validated_data=serializer.validated_data)
                return Response(serializer.data, status = status.HTTP_200_OK)
            except:
                return Response(
                    {
                        'error' : "Algo correu mal ao atualizar o utilizador.",
                        "data" : serializer.errors
                    }, 
                    status = status.HTTP_404_NOT_FOUND
                )
        else:
            return Response({'error' : serializer.errors}, status = status.HTTP_400_BAD_REQUEST) 
    return Response({'error' : "Utilizador não encontrado"}, status = status.HTTP_404_NOT_FOUND) 

@swagger_auto_schema(       
    method='get',
    operation_description="List all users"
)
@api_view(['GET'])
@permission_classes([IsAdminOrUpper])
def list_all_users(request):
    if(request.user.is_superuser):
        users = User.objects.all().annotate(
            group=F('group_user_id')
        ).values('id','is_superuser','username','email','is_staff','status','group')
    else:
        users = User.objects.filter(group_user_id=request.user.group_user_id).values('id','username','email','is_staff','status')
    if users is None:
        return Response({"error" : "Nenhum utilizador encontrado!"},status=status.HTTP_404_NOT_FOUND)
    return Response({"users" : users, "message" : "Utilizadores encontrados com sucesso!"}, status=status.HTTP_200_OK)  

@swagger_auto_schema(
    method='post',
    request_body=CreateUserSerializer,
    operation_description="Create a User"
)    
@api_view(['POST'])
#@parser_classes([MultiPartParser])
@permission_classes([IsAdminOrUpper])
def create_new_user(request, *args, **kwargs): 
    serializer = CreateUserSerializer(data=request.data, context={'request': request})
    data = {}
    if serializer.is_valid():
        try:
            serializer.save()
            user = User.objects.filter(id=serializer.data.get('id')).first()
            user.set_password("12345678")
            user.save()
            data['response'] = "Registration Successful!"
            data['id'] = serializer.data.get('id')
            data['username'] = serializer.data.get('username')
            data['email'] = serializer.data.get('email')  
            data['is_staff'] = serializer.data.get('is_staff')
            data['status'] = serializer.data.get('status')
            if request.user and request.user.is_superuser:
                data['is_superuser'] = serializer.data.get('is_superuser')
                data['group'] = serializer.data.get('group_user') if serializer.data.get('group_user') is not None else None
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as error:
            return Response({'erro' : error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
    else:
        data = serializer.errors
        return Response({'erro' : data}, status=status.HTTP_400_BAD_REQUEST)   
    
@swagger_auto_schema(
    method='post',
    operation_description="Delete a user"
) 
@api_view(['POST'])
@permission_classes([IsAdminOrUpper])
def remove(request, *args, **kwargs):
    user = User.objects.filter(id=kwargs.get('pk')).first()
    if user is None:
        return Response({"error" : "User does not exist!"},status=status.HTTP_404_NOT_FOUND)
    try:
        user.delete()
    except Exception as e:
        return Response({"error" : e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"success" : "Utilizador eliminado comm sucesso!"}, status=status.HTTP_200_OK)
    
@swagger_auto_schema(
    method='post',
    request_body=EditUserSerializer,
    operation_description="Edit a User "
)    
@api_view(['POST'])
@permission_classes([IsAdminOrUpper])
#@parser_classes([MultiPartParser])
#@permission_classes([isEqualOrUpperPermission])
def edit_user(request, *args, **kwargs):
    user = User.objects.filter(id=kwargs['pk']).first()
    if user is not None:
        serializer = EditUserSerializer(data = request.data, partial=True, context={'request': request})   
        if serializer.is_valid():
            try:         
                serializer.update(instance = user, validated_data=serializer.validated_data)
                newUser = User.objects.filter(id=kwargs['pk']).first()
                response = {}
                response['id'] = newUser.id
                response['username'] = newUser.username
                response['email'] = newUser.email
                response['is_staff'] = newUser.is_staff
                response['status'] = newUser.status
                if request.user and request.user.is_superuser:
                    response['is_superuser'] = newUser.is_superuser
                    response['group'] = user.group_user.id if user.group_user is not None else None
                return Response(response, status = status.HTTP_200_OK)
            except:
                return Response({'error' : "Algo correu mal ao atualizar o utilizador","data" : serializer.errors}, status = status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error' : serializer.errors}, status = status.HTTP_400_BAD_REQUEST) 
    return Response({'error' : "Utilizador não encontrado"}, status = status.HTTP_404_NOT_FOUND) 

def getRole(user):
    role = 'user'
    if user.is_superuser:
        role = 'super'
    elif user.is_staff:
        role = 'staff'
    return role