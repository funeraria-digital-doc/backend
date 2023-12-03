from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import base64
from io import BytesIO
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from babel.dates import format_datetime
from groups.models import Group
import io
import logging
from dateutil.parser import parse
logger = logging.getLogger(__name__)

recordLabels = {
    "WOMAN":    'Feminino',
    "MALE":     'Masculino',
    "OTHER":    'Outro',
    "SINGLE":   'Solteiro/a',
    "MARIED":   'Casado/a',
    "DIVORCED": 'Divorciado/a',
    "WIDOWER":  'Viúvo/a',
    "INACTIVE": 'Inativo',
    "ACTIVE":   'Ativo',
    "PENDING":  'Pendente',
    "COMPLETED":'Terminado',
    "ARCHIVED": 'Arquivado'
}

userLabels = {
    "1": "Inativo",
    "2": "Ativo",
    "3": "Suspenso"
}

def getFullDate(formatVar, full):
    format = ''
    if any(substring in formatVar for substring in ['DAY', 'DAYS']):
        format += "%d" if full else '%d'
    if any(substring in formatVar for substring in ['MONTH', 'MONTHS']):
        if format:
            format += "' de '" if full else '/'
        format += '%B' if full else '%m'
    if any(substring in formatVar for substring in ['YEAR', 'YEARS']):
        if format:
            format += "' de '" if full else '/'
        format += '%Y'
    if any(substring in formatVar for substring in ['HOUR', 'HOURS']):
        if format:
            format += "' às '" if full else ' '
        format += "%H' horas'" if full else '%H'
    if any(substring in formatVar for substring in ['MINUTE', 'MINUTES']):
        if format and any(substring in formatVar for substring in ['HOUR', 'HOURS']) and any(substring in formatVar for substring in ['SECOND', 'SECONDS']) :
            format += "', '" if full else ':'
        elif format and any(substring in formatVar for substring in ['HOUR', 'HOURS']):
            format += "' e '" if full else ':'
        elif format:
            format += "' aos '" if full else ' '
        format += "%M' minutos'" if full else '%M'
    if any(substring in formatVar for substring in ['SECOND', 'SECONDS']):
        if format and any(substring in formatVar for substring in ['HOUR', 'HOURS', 'MINUTE', 'MINUTES']):
            format += "' e '" if full else ':'
        elif format:
            format +="' aos '" if full else ' '
        format += "%S' segundos'" if full else '%S'
    return format

def convert_to_babel_format(python_format):
    # Mapping of Python strftime directives to Babel's pattern syntax
    format_mapping = {
        '%a': 'EEE',
        '%A': 'EEEE',
        '%w': 'e',
        '%d': 'dd',
        '%b': 'MMM',
        '%B': 'MMMM',
        '%m': 'MM',
        '%y': 'yy',
        '%Y': 'yyyy',
        '%H': 'HH',
        '%I': 'hh',
        '%p': 'a',
        '%M': 'mm',
        '%S': 'ss'
    }

    babel_format = python_format
    for py_directive, babel_pattern in format_mapping.items():
        babel_format = babel_format.replace(py_directive, babel_pattern)

    return babel_format

def editDocument(template, data):
    from django.shortcuts import render
    import zipfile
    doc_variables = get_doc_variables(template, True, True)
    if len(doc_variables['vars']) ==  0 and len(data['files']) == 0:
        return Response({"error" : "No variables found"}, status = status.HTTP_404_NOT_FOUND)
    not_found_keys = []
    edited_keys_array = []
    edited_keys = {}
    context = {}
    
    for var in doc_variables['vars']:
        edited_value = data['variables'][var]
        if type(edited_value) is list:
            edited_str = ""
            for edited in edited_value:
                if edited_str == "":
                    edited_str = edited
                else:
                    edited_str += ", " + edited

            context[var] = edited_str
        else:
            context[var] = edited_value
        edited_keys_array.append(context[var])
    file_validations = {item['name']: item for item in template.get('file_validations')}
    base64_string = template.get('file').split(',')[1]
    docx_bytes = base64.b64decode(base64_string)
    word_zip = zipfile.ZipFile(io.BytesIO(docx_bytes), 'r')
    for file in data['files']:
        new_file = getImage(data['files'][file])
        for fileItem in word_zip.filelist:
            if fileItem.filename.startswith('word/media/') and fileItem.filename.replace('word/media/', '').split('.')[0] == file_validations[file].get('name').replace('Imagem ', 'image'):
                img_data = io.BytesIO(word_zip.read(fileItem))
                doc_variables['doc'].replace_media(img_data,new_file)
    not_used_vars = []
    for doc_var in doc_variables['vars']:
        if doc_var not in edited_keys_array:
            not_used_vars.append(doc_var)
            edited_keys[doc_var] = '{{ ' + doc_var + ' }}'
    if len(context) > 0 :
        doc_variables['doc'].render(context)
    return {'not_found_keys' : not_found_keys, 'edited_keys' : edited_keys_array, "doc" : doc_variables['doc']}

def getImage(file):
    from PIL import Image
    img_data = base64.b64decode(file)
    img_io = BytesIO(img_data) 
    img = Image.open(img_io)
    img_io = BytesIO()
    img.save(img_io, format='PNG')  # or another format ('JPEG', etc.)
    img_io.seek(0)
    return img_io

def getDbKeysToDoc(request, template, changeVariablesObject, doc_variables, keys_missing, record):
    validations = {item['name']: item for item in template.get('validations')}
    file_validations = {item['name']: item for item in template.get('file_validations')}
    for variable in doc_variables['vars']:
        if variable in request.data.get('validations'):
            changeVariablesObject['variables'][variable] = request.data.get('validations')[variable]
    for fileKey,fileValidation in file_validations.items():
        if not fileKey in changeVariablesObject['files']:
            if "is_blocked" in fileValidation and fileValidation.get("is_blocked"):
                continue 
            if "is_field_custom" in fileValidation and not fileValidation.get("is_field_custom") and "db_collection" in fileValidation:
                if fileValidation.get("db_collection") == "USERS":
                    userField = getattr(request.user, fileValidation.get("db_field_reference"), "")
                    changeVariablesObject['files'][fileKey] = userField.split(',')[1] if userField else userField
                if fileValidation.get("db_collection") == "GROUPS":
                    group = Group.objects.filter(id= template.get('group_id')).values(fileValidation.get("db_field_reference")).first()
                    if fileValidation.get("db_field_reference") in group:
                        groupField = group.get(fileValidation.get("db_field_reference"))
                        changeVariablesObject['files'][fileKey] = groupField.split(',')[1] if groupField else groupField
                if fileValidation.get("db_collection") == "RECORDS" and fileValidation.get("db_field_reference") in record:
                    recordField = record.get(fileValidation.get("db_field_reference"))
                    changeVariablesObject['files'][fileKey] = recordField.split(',')[1] if recordField else recordField
            else: 
                changeVariablesObject['files'][fileKey] = request.data.get('file_validations')[fileKey].split(',')[1]     
    for key,validation in validations.items():
        if not key in changeVariablesObject['variables']:
            if "is_field_custom" in validation and not validation.get("is_field_custom") and "db_collection" in validation:
                if validation.get("db_collection") == "USERS":
                    if 'field_type' in validation and validation.get("field_type") in ["SELECT"]:
                        changeVariablesObject['variables'][key] = getLabel(getattr(request.user, validation.get("db_field_reference"), ""),userLabels)
                    else:
                        changeVariablesObject['variables'][key] = getattr(request.user, validation.get("db_field_reference"), "")
                if validation.get("db_collection") == "GROUPS":
                    group = Group.objects.filter(id= template.get('group_id')).values(validation.get("db_field_reference")).first()
                    if validation.get("db_field_reference") in group:
                        changeVariablesObject['variables'][key] = group.get(validation.get("db_field_reference"))
                if validation.get("db_collection") == "RECORDS" and validation.get("db_field_reference") in record:
                    if 'field_type' in validation and validation.get("field_type") in ["SELECT"]:
                        changeVariablesObject['variables'][key] = getLabel(record.get(validation.get("db_field_reference")),recordLabels)
                    elif 'field_type' in validation and validation.get("field_type") in ["FILE"]:
                        changeVariablesObject['variables'][key] = record.get(validation.get("db_field_reference")).split(',')[1]
                    else:
                        changeVariablesObject['variables'][key] = record.get(validation.get("db_field_reference"))
                if validation.get("db_collection") == "SYSTEM":
                    if validation.get("db_field_reference") == 'CURRENT_DATE':
                        getFormat =  getFullDate(validation.get('format'), not validation.get('is_date_numeric'))
                        nowDate = datetime.now()
                        dateFormat = convert_to_babel_format(getFormat).replace("''", "")
                        date = format_datetime(nowDate,dateFormat, locale='pt_PT')
                        changeVariablesObject['variables'][key] = date
                if 'field_type' in validation and validation.get("field_type") in ["DATE", "TIME", 'DATETIME'] and 'format' in validation and key in changeVariablesObject['variables']:
                    date = ''
                    if changeVariablesObject['variables'][key]:
                        if 'is_date_numeric' in validation and not validation.get('is_date_numeric'):
                            date = getNumericDate(validation, request, key, changeVariablesObject['variables'])
                        else: 
                            date = parse(str(changeVariablesObject['variables'][key])).strftime(getFullDate(validation.get('format'), False)) if isinstance(changeVariablesObject['variables'][key], str) else changeVariablesObject['variables'][key].strftime(getFullDate(validation.get('format'), False))
                    changeVariablesObject['variables'][key] = date 
                            
            else:
                keys_missing.append(key) 
                continue
        else: 
            if not key in changeVariablesObject['variables'] or changeVariablesObject['variables'] == "" or changeVariablesObject['variables'] == None:
                keys_missing.append(key)
                continue
            if 'field_type' in validation and validation.get("field_type") in ["DATE", "TIME", 'DATETIME'] and 'format' in validation:
                date = ''
                if changeVariablesObject['variables'][key] is not None:
                    if 'is_date_numeric' in validation and not validation.get('is_date_numeric'):
                        date = getNumericDate(validation, request, key, changeVariablesObject['variables'])
                    else: 
                        date = parse(str(changeVariablesObject['variables'][key])).strftime(getFullDate(validation.get('format'), False)) if isinstance(changeVariablesObject['variables'][key], str) else changeVariablesObject['variables'][key].strftime(getFullDate(validation.get('format'), False))
                changeVariablesObject['variables'][key] = date 

def getNumericDate(validation, request, key, changeVariablesObject):
    getFormat =  getFullDate(validation.get('format'), False)
    dateValue = request.data.get('validations')[key] if validation.get("is_field_custom") else str(changeVariablesObject[key].strftime(getFormat))
    newdate = datetime.strptime(dateValue, getFormat)
    dateFormat = convert_to_babel_format(getFullDate(validation.get('format'), True)).replace("''", "")
    date = format_datetime(newdate,dateFormat, locale='pt_PT')
    return date

def get_doc_variables(template, getDoc, getVars):
    base64_string = template.get('file').split(',')[1]
    docx_bytes = base64.b64decode(base64_string)
    byte_stream = io.BytesIO(docx_bytes)
    doc = DocxTemplate(byte_stream)
    variables = doc.get_undeclared_template_variables() if doc.get_undeclared_template_variables() else []
    if getDoc and getVars:
        return {
            'vars' : variables,
            'doc' : doc
        }
    if getDoc:
         return doc
    if getVars:
        return variables
    
def hasDuplicates(validations):
    seen = set()
    duplicatedKeys = []
    for validation in validations:
       
        if validation['name'] not in seen:
            duplicatedKeys.append(validation['name'])
            seen.add(validation['name'])
        else:
            return Response({"errors" : {'validations' : "Duplicate keys in validations field", 'keys' : duplicatedKeys}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return False

def getLabel(val, labels):
    return labels[val] if val in labels else ''
