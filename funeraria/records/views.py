import json
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
#from rest_framework.permissions import permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from records.models import Record
from records.serealizers import RecordCreateSerializer, RecordUpdateSerializer

from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import  JSONParser
import logging
logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='post',
    request_body=RecordCreateSerializer,
    operation_description="Create a new Record"
)    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create(request, *args, **kwargs):
    record = {}
    for requestPart in request.data:
        record[requestPart] = request.data.get(requestPart)
    logger.info(request.user.__dict__)
    record['group'] = request.user.group_user_id if request.user.group_user_id else None
    serializer = RecordCreateSerializer(data=record)
    finalRecord = {}
    
    try:
        if serializer.is_valid():
            try:
                serializer.save()
                finalRecord['record']  = serializer.data
            except Exception as e:
                finalRecord['errors']   = serializer.errors
                return Response(finalRecord, status=status.HTTP_400_BAD_REQUEST)            
        else: 
            logger.info(serializer.errors) 
            finalRecord['errors'] = serializer.errors
            return Response(finalRecord, status=status.HTTP_400_BAD_REQUEST)    
    except Exception as e:
        finalRecord['errors']   = "erro no is_valid"
        #raise serializer.errors
    return Response(finalRecord, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="View details of a record"
) 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view(request, *args, **kwargs):
    record = Record.objects.filter(pk=kwargs.get('pk')).values().first()
    if record is None:
        return Response({"errors" : "Declaração não existe!"}, status = status.HTTP_404_NOT_FOUND)
    return Response(record, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    request_body=RecordUpdateSerializer,
    operation_description="Update a Record"
)    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update(request, *args, **kwargs):
    recordInstance = Record.objects.filter(pk=kwargs.get('pk')).first() 
    record = request.data
    serializer = RecordUpdateSerializer(data = record,instance=recordInstance, partial=True)   
    if serializer.is_valid():
        if record is None:
                return Response({"errors" : "Declaração não existe!"}, status = status.HTTP_404_NOT_FOUND)
        try:            
            serializer.update(instance = recordInstance, validated_data=serializer.validated_data)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except:
            return Response({'errors' : "Algo correu mal a atualizar a declaração","data" : serializer.errors}, status = status.HTTP_404_NOT_FOUND)
    else:
        return Response({'errors' : serializer.errors}, status = status.HTTP_400_BAD_REQUEST)   

@swagger_auto_schema(
    method='post',
    operation_description="Delete a record"
) 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove(request, *args, **kwargs):
    record = Record.objects.filter(id=kwargs.get('pk')).first()
    if record is None:
        return Response({"errors" : "Declaração não existe!"},status=status.HTTP_404_NOT_FOUND)
    record.delete()
    return Response({"success" : "Declaração eliminada com sucesso!"}, status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='get',
    operation_description="List all records"
) 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list(request, *args, **kwargs):
    if request.user.is_superuser:
        records = Record.objects.all().values('id','name','family_member_phone','gender','group_id','email','status')
        return Response(records, status = status.HTTP_200_OK)
    else:
        records = Record.objects.filter(group_id=request.user.group_user_id).values('id','name','family_member_phone','gender','group_id','email','status')
        return Response(records, status = status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Update records status to arquived"
) 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateManyStatus(request, *args, **kwargs):
    ids = request.data
    try:
        Record.objects.filter(id__in=ids).update(status="ARCHIVED")
        return Response({"success" : True, "message":"Declarações alteradas com sucesso!"}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.info(e) 
        return Response({"success" : False, "errors" : "Erro ao atualizar declarações!"}, status=status.HTTP_400_BAD_REQUEST)
       




