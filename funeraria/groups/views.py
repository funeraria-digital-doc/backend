import logging
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from groups.serealizers import GroupCreateSerializer, GroupUpdateSerializer
from groups.models import Group
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.decorators import parser_classes
from django.core.cache import cache
logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='post',
    request_body=GroupCreateSerializer,
    operation_description="Create a new Group"
)    
@api_view(['POST'])
def create(request, *args, **kwargs):
    data = JSONParser().parse(request)
    serializer = GroupCreateSerializer(data=data)
    group = {}
    try:
        if serializer.is_valid():
            try:
                serializer.save()
                group['group']  = dict({
                    'id' : serializer.instance.id,
                    'name' : serializer.instance.name
                })
                group['msg']  = "Group created successfully"
                return Response(group, status = status.HTTP_200_OK)
            except Exception as e:
                group['error']   = serializer.errors
                return Response(group, status=status.HTTP_400_BAD_REQUEST)            
        else: 
            group['error'] = serializer.errors
            return Response(group, status = status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        group['error']   = "erro no is_valid"
        #raise serializer.errors
    return Response(group, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    operation_description="View details of a group"
) 
@api_view(['GET'])
def view(request, *args, **kwargs):
    group = Group.objects.filter(pk=kwargs.get('pk')).values().first()
    if group is None:
        return Response({"error" : "Group does not exist!"}, status = status.HTTP_200_OK)
    return Response(group, status = status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='post',
    request_body=GroupUpdateSerializer,
    operation_description="Update a Group"
)    
@api_view(['POST'])
def update(request, *args, **kwargs):
    group = Group.objects.filter(pk=kwargs.get('pk')).first()  
    serializer = GroupUpdateSerializer(data = request.data,instance=group, partial=True)   
    if serializer.is_valid():
        if group is None:
                return Response({"error" : "Group does not exist!"}, status = status.HTTP_404_NOT_FOUND)
        try:            
            serializer.update(instance = group, validated_data=serializer.validated_data)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except:
            return Response({'error' : "something went wrong updating group","data" : serializer.errors}, status = status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error' : serializer.errors}, status = status.HTTP_400_BAD_REQUEST)   

@swagger_auto_schema(
    method='post',
    operation_description="Delete a group"
) 
@api_view(['POST'])
def remove(request, *args, **kwargs):
    group = Group.objects.filter(id=kwargs.get('pk')).first()
    if group is None:
        return Response({"error" : "Group does not exist!"},status=status.HTTP_404_NOT_FOUND)
    try:
        group.delete()
    except Exception as e:
        logger.info("Error deleting", e)
    return Response({"success" : "Group deleted successfully!"}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="List all groups"
) 
@api_view(['GET'])
def list(request, *args, **kwargs):
    cache_key = 'all_groups'
    groups = cache.get(cache_key)
    if not groups:
        logger.info('não tinha cache')
        groups = Group.objects.all().values('id','name')
        cache.set(cache_key, groups)
    else:
        cache.touch(cache_key)
    groups = Group.objects.all().values('id','name')
    return Response(groups, status = status.HTTP_200_OK)



