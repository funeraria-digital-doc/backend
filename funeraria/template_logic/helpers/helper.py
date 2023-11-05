from docxtpl import DocxTemplate
import base64
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

def editDocument(template, data, saveDocument):
    from django.shortcuts import render
    doc_variables = get_doc_variables(template, True, True)
    if len(doc_variables['vars']) ==  0:
        return Response({"error" : "No variables found"}, status = status.HTTP_404_NOT_FOUND)
    not_found_keys = []
    edited_keys_array = []
    edited_keys = {}
    context = {}
    for var in doc_variables['vars']:
        edited_value = data[var]
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

    not_used_vars = []
    for doc_var in doc_variables['vars']:
        if doc_var not in edited_keys_array:
            not_used_vars.append(doc_var)
            edited_keys[doc_var] = '{{ ' + doc_var + ' }}'
    if len(context) > 0 :
        doc_variables['doc'].render(context=context)
        if saveDocument:
            doc_variables['doc'].save('media/' + template.get('file'))
    return {'not_found_keys' : not_found_keys, 'edited_keys' : edited_keys_array, "doc" : doc_variables['doc']}

def getDbKeysToDoc(request, template, template_validations, changeVariablesObject, doc_variables, keys_missing, record):
    validations = {item['name']: item for item in template_validations}
    for variable in doc_variables['vars']:
        if variable in request.data.get('validations'):
            changeVariablesObject[variable] = request.data.get('validations')[variable]
    for key,validation in validations.items():
        if not key in changeVariablesObject:
            if "is_field_custom" in validation and not validation.get("is_field_custom") and "db_collection" in validation:
                if validation.get("db_collection") == "USERS":
                    if 'field_type' in validation and validation.get("field_type") in ["SELECT"]:
                        changeVariablesObject[key] = getLabel(getattr(request.user, validation.get("db_field_reference"), ""),userLabels)
                    else:
                        changeVariablesObject[key] = getattr(request.user, validation.get("db_field_reference"), "")
                if validation.get("db_collection") == "GROUPS":
                    group = Group.objects.filter(id= template.get('group_id')).values(validation.get("db_field_reference")).first()
                    if validation.get("db_field_reference") in group:
                        changeVariablesObject[key] = group.get(validation.get("db_field_reference"))
                if validation.get("db_collection") == "RECORDS" and validation.get("db_field_reference") in record:
                    if 'field_type' in validation and validation.get("field_type") in ["SELECT"]:
                        changeVariablesObject[key] = getLabel(record.get(validation.get("db_field_reference")),recordLabels)
                    else:
                        changeVariablesObject[key] = record.get(validation.get("db_field_reference"))

              
        if 'field_type' in validation and validation.get("field_type") in ["DATE", "TIME", 'DATETIME'] and 'format' in validation:
            if 'is_date_numeric' in validation and not validation.get('is_date_numeric'):
                logger.info("cenas - " + key)
                getFormat =  getFullDate(validation.get('format'), False)
                dateValue = request.data.get('validations')[key] if validation.get("is_field_custom") else str(changeVariablesObject[key].strftime(getFormat))
                newdate = datetime.strptime(dateValue, getFormat)
                dateFormat = convert_to_babel_format(getFullDate(validation.get('format'), True)).replace("''", "")
                logger.info(dateFormat)
                date = format_datetime(newdate,dateFormat, locale='pt_PT')
                logger.info(date)
            else: 
                if isinstance(changeVariablesObject[key], str):
                    date = parse(str(changeVariablesObject[key])).strftime(getFullDate(validation.get('format'), False))
                else: 
                    date = changeVariablesObject[key].strftime(getFullDate(validation.get('format'), False))
            changeVariablesObject[key] = date
        # if not validation.get("is_field_custom") and 'field_type' in validation and validation.get("field_type") in ["SELECT"]:
        #     logger.info('get labels ')
        if not key in changeVariablesObject or changeVariablesObject == "" or changeVariablesObject == None:
            keys_missing.append(key)


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
