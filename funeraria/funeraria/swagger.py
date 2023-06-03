from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.decorators import api_view, renderer_classes, authentication_classes
from rest_framework import response, schemas
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

@api_view()
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer])
@authentication_classes((TokenAuthentication, SessionAuthentication))
def schema_view(request):
    generator = schemas.SchemaGenerator(title='Test API')
    return response.Response(generator.get_schema(request=request))