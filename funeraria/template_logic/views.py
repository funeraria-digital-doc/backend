from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from docxtpl import DocxTemplate
from template_logic.variables import get_var_types
from groups.models import Group
from template_logic.serealizers import UploadSerializer
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from template_logic.models import TemplateLogic
# Create your views here.

@api_view(['GET'])
def list_templates(request):
    templates = TemplateLogic.objects.all().values()
    if(templates.count() > 0):
        return Response({'data' : templates}, status=status.HTTP_200_OK)
    return Response({'error' : 'No templates available'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_variables(request, *args, **kwargs):
    template = TemplateLogic.objects.filter(id=kwargs.get('pk')).values().first()
    if template is None:
        return Response({"error" : "Template does not exist!"}, status = status.HTTP_404_NOT_FOUND)
    variables = get_doc_variables(template)['vars']
    return Response(variables, status = status.HTTP_200_OK)
    

@api_view(['POST'])
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


@api_view(['PATCH'])
def edit_variables(request, *args, **kwargs):
    #var_types = get_var_types()
    template = TemplateLogic.objects.filter(id=kwargs.get('pk')).values().first()
    if template is None:
        return Response({"error" : "Template does not exist!"}, status = status.HTTP_404_NOT_FOUND)
    doc_variables = get_doc_variables(template)
    if len(doc_variables['vars']) ==  0:
        return Response({"error" : "No variables found"}, status = status.HTTP_404_NOT_FOUND)
    not_found_keys = []
    edited_keys = []
    for key_var,var_key_text in enumerate(request.data):
        if  var_key_text in doc_variables['vars']:
            print(doc_variables['doc'].paragraphs)
            for key , paragraph in enumerate(doc_variables['doc'].paragraphs):
                if '{{ ' + var_key_text + ' }}' in paragraph.text:
                    doc_variables['doc'].paragraphs[key].text = paragraph.text.replace('{{ ' + var_key_text + ' }}', '{{ ' + request.data[var_key_text] + ' }}' )
                    print(paragraph.text)
                    edited_keys.append(var_key_text)
        else : 
            not_found_keys.append(var_key_text)
    
    if len(edited_keys) > 0 :
        print(template['file'])
        doc_variables['doc'].save('media/' + template['file'])
    return Response({'not_found_keys' : not_found_keys, 'edited_keys' : edited_keys}, status=status.HTTP_200_OK)

@api_view(['POST'])
def download(request):
    return Response({'data' : "download"}, status=status.HTTP_200_OK)
@api_view(['PATCH'])
def edit(request):
    return Response({'data' : "edit"}, status=status.HTTP_200_OK)
@api_view(['DELETE'])
def remove(request):
    return Response({'data' : "remove"}, status=status.HTTP_200_OK)


def get_doc_variables(template):
    doc = DocxTemplate('media/' + template['file'])
    variables = doc.get_undeclared_template_variables() if doc.get_undeclared_template_variables() else []
    return {
        'vars' : variables,
        'doc' : doc
    }





    # file = request.data['file']
    # print(file)
    # doc = DocxTemplate(file)
    # print(doc.get_undeclared_template_variables())
    # doc.render(context={'name': 'cenas' , 'last' : 'conseguiiiii'})
    # doc.save('C:/Users/joaor/Desktop/django_projects/files/teste_1.docx')





    
    
    
