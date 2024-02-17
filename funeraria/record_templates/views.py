from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from records.models import Record
from template_logic.models import TemplateLogic
import logging
logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='get',
    operation_description="List all Templates for the record"
) 
@api_view(['GET'])
#@permission_classes()
#[IsAuthenticated]
def get_record_templates(request, *args, **kwargs):
    record = Record.objects.filter(id=kwargs.get('pk')).values('group_id').first()
    if record is None:
        return Response({'success': False}, status=status.HTTP_404_NOT_FOUND) 
    templates = TemplateLogic.objects.filter(group_id=record.get('group_id')).values('id', 'title', 'validations', 'file_validations', 'send_type')
    return Response({'data': templates}, status = status.HTTP_200_OK)

