from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from docxtpl import DocxTemplate
from template_logic.serealizers import UploadSerializer

from template_logic.models import TemplateLogic
# Create your views here.

@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def template_upload(request):

    form = UploadSerializer(request.POST, request.FILES)
    print(form.is_valid())
    if form.is_valid():
        # file is saved
        form.save()
        return Response(form.slug, status=status.HTTP_200_OK)
    else:
        
        return Response(form._get_validation_exclusions(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # file = request.data['file']
    # print(file)
    # doc = DocxTemplate(file)
    # print(doc.get_undeclared_template_variables())
    # doc.render(context={'name': 'cenas' , 'last' : 'conseguiiiii'})
    # doc.save('C:/Users/joaor/Desktop/django_projects/files/teste_1.docx')
    
    
    
