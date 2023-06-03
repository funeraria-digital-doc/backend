import json
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.decorators import parser_classes
from records.models import Record
from records.serealizers import RecordCreateSerializer, RecordUpdateSerializer

from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import  JSONParser

@swagger_auto_schema(
    method='post',
    request_body=RecordCreateSerializer,
    operation_description="Create a new Record"
)    
@api_view(['POST'])
@parser_classes([MultiPartParser])
def create(request, *args, **kwargs):
    record = {}
    for requestPart in request.POST:
        record[requestPart] = request.POST.get(requestPart)
    for requestFile in request.FILES:
        record[requestFile] = request.FILES.get(requestFile)
       
    serializer = RecordCreateSerializer(data=record)
    finalRecord = {}
    try:
        if serializer.is_valid():
            try:
                serializer.save()
                finalRecord['record']  = serializer.data
                finalRecord['msg']  = "Record created successfully"
            except Exception as e:
                print(e)
                if serializer.data['photo'] is not None and serializer.data['photo'] == record['photo']:
                    record
                finalRecord['error']   = serializer.errors
                return Response(finalRecord, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        else: 
            finalRecord['error'] = serializer.errors
    except Exception as e:
        finalRecord['error']   = "erro no is_valid"
        #raise serializer.errors
    return Response({'record' : finalRecord}, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="View details of a record"
) 
@api_view(['GET'])
def view(request, *args, **kwargs):
    record = Record.objects.filter(pk=kwargs.get('pk')).values().first()
    if record is None:
        return Response({"error" : "Record does not exist!"}, status = status.HTTP_404_NOT_FOUND)
    return Response(record, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    request_body=RecordUpdateSerializer,
    operation_description="Update a Record"
)    
@api_view(['POST'])
@parser_classes([MultiPartParser])
def update(request, *args, **kwargs):
    recordInstance = Record.objects.filter(pk=kwargs.get('pk')).first() 
    record = {}
    for requestPart in request.POST:
        record[requestPart] = request.POST.get(requestPart)
    for requestFile in request.FILES:
        record[requestFile] = request.FILES.get(requestFile)
    serializer = RecordUpdateSerializer(data = record,instance=recordInstance, partial=True)   
    if serializer.is_valid():
        if record is None:
                return Response({"error" : "Record does not exist!"}, status = status.HTTP_404_NOT_FOUND)
        try:            
            serializer.update(instance = recordInstance, validated_data=serializer.validated_data)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except:
            return Response({'error' : "something went wrong updating record","data" : serializer.errors}, status = status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error' : serializer.errors}, status = status.HTTP_400_BAD_REQUEST)   

@swagger_auto_schema(
    method='delete',
    operation_description="Delete a record"
) 
@api_view(['DELETE'])
def remove(request, *args, **kwargs):
    record = Record.objects.filter(id=kwargs.get('pk')).first()
    if record is None:
        return Response({"error" : "Record does not exist!"},status=status.HTTP_404_NOT_FOUND)
    record.delete()
    return Response({"success" : "Record deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='get',
    operation_description="List all records"
) 
@api_view(['GET'])
def list(request, *args, **kwargs):
    records = Record.objects.all().values()
    return Response(records, status = status.HTTP_200_OK)



        




