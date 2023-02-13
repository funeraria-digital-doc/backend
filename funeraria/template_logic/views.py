from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from docxtpl import DocxTemplate
from template_logic.variables import get_var_types
from groups.models import Group
from template_logic.serealizers import UploadSerializer, EditSerializer
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework import generics
from template_logic.models import TemplateLogic
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.decorators import parser_classes

@swagger_auto_schema(
    method='get',
    operation_description="List all templates"
) 
@api_view(['GET'])
def list_templates(request):
    templates = TemplateLogic.objects.all().values()
    if(templates.count() > 0):
        return Response({'data' : templates}, status=status.HTTP_200_OK)
    return Response({'error' : 'No templates available'}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    operation_description="Get all variables from a template"
) 
@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_variables(request, *args, **kwargs):
    template = TemplateLogic.objects.filter(id=kwargs.get('pk')).values().first()
    if template is None:
        return Response({"error" : "Template does not exist!"}, status = status.HTTP_404_NOT_FOUND)
    variables = get_doc_variables(template)['vars']
    return Response(variables, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    request_body=UploadSerializer,
    operation_description="Upload a document template"
)    
@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload(request):
    data = {
        'title' : request.POST.get('title'),
        'group' : request.POST.get('group'),
        'file' : request.FILES.get('file'),
    }
    form = UploadSerializer(data = data)
    if form.is_valid():
        if data['file']:
            myfile = data['file']
            fs = FileSystemStorage()
            if fs.exists(myfile.name):
                return Response({'error' : 'File name already exists!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            form.save()
            return Response({'data' : form.data}, status=status.HTTP_200_OK)
        else:
            return Response("no valid 2", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'errors' : form.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(       
    method='patch',
    operation_description="Edit template variables",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties= {'variable_old': openapi.Schema(title="variable_new",type=openapi.TYPE_STRING)},
    ),
)
@api_view(['PATCH'])
@parser_classes([JSONParser])
def edit_variables(request, *args, **kwargs):
    #var_types = get_var_types()
    print(request.data)
    print(args)
    template = TemplateLogic.objects.filter(id=kwargs.get('pk')).values().first()
    if template is None:
        return Response({"error" : "Template does not exist!"}, status = status.HTTP_404_NOT_FOUND)
    doc_variables = get_doc_variables(template)
    if len(doc_variables['vars']) ==  0:
        return Response({"error" : "No variables found"}, status = status.HTTP_404_NOT_FOUND)
    not_found_keys = []
    edited_keys_array = []
    edited_keys = {}
    char_remov = ["-"," "]
    for key_var,var_key_text in enumerate(request.data):
        if  var_key_text in doc_variables['vars']:
            for key , paragraph in enumerate(doc_variables['doc'].paragraphs):
                if '{{ ' + var_key_text + ' }}' in paragraph.text or '{{' + var_key_text + '}}' in paragraph.text:
                    edited_value = request.data[var_key_text]
                    for char in char_remov:
                        edited_value = edited_value.replace(char, "_")
                    edited_keys[var_key_text] = '{{ ' + edited_value + ' }}'
                    edited_keys_array.append(var_key_text)
        else : 
            not_found_keys.append(var_key_text)

    not_used_vars = []
    for doc_var in doc_variables['vars']:
        if doc_var not in edited_keys_array:
            not_used_vars.append(doc_var)
            edited_keys[doc_var] = '{{ ' + doc_var + ' }}'
    
    if len(edited_keys) > 0 :
        doc_variables['doc'].render(context=edited_keys)
        doc_variables['doc'].save('media/' + template['file'])
    return Response({'not_found_keys' : not_found_keys, 'edited_keys' : edited_keys_array}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    operation_description="Download a Template with all replaced variables from a registered death"
) 
@api_view(['POST'])
def download(request):
    return Response({'data' : "download"}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='patch',
    request_body=EditSerializer,
    operation_description="Edit a template"
)    
@api_view(['PATCH'])
@parser_classes([MultiPartParser])
def edit(request, *args, **kwargs):
    template = TemplateLogic.objects.filter(pk=kwargs.get('pk')).first()  
    serializer = UploadSerializer(data = request.data,instance=template, partial=True)   
    print(serializer.is_valid())
    if serializer.is_valid():
        if template is None:
                return Response({"error" : "Template does not exist!"}, status = status.HTTP_404_NOT_FOUND)
        try:            
            serializer.update(instance = template, validated_data=serializer.validated_data)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except:
            return Response({'error' : "something went wrong updating template","data" : serializer.errors}, status = status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error' : serializer.errors}, status = status.HTTP_400_BAD_REQUEST)   
    

@swagger_auto_schema(
    method='delete',
    operation_description="Delete a Template"
) 
@api_view(['DELETE'])
def remove(request, *args, **kwargs):   
    template = TemplateLogic.objects.filter(id=kwargs.get('pk')).first()
    if template is None:
        return Response({"error" : "Template does not exist!"},status=status.HTTP_404_NOT_FOUND)
    try:
        template.delete()
        return Response({"success" : "Template deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except:
        return Response({"success" : "An error as occured. Try again later!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def get_doc_variables(template):
    doc = DocxTemplate('media/' + template['file'])
    variables = doc.get_undeclared_template_variables() if doc.get_undeclared_template_variables() else []
    return {
        'vars' : variables,
        'doc' : doc
    }







    
    
    
