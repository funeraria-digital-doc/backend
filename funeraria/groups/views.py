import logging
from funeraria.permissions import IsSuperUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from groups.serealizers import GroupCreateSerializer, GroupUpdateSerializer
from groups.models import Group
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='post',
    request_body=GroupCreateSerializer,
    operation_description="Create a new Group"
)    
@api_view(['POST'])
@permission_classes([IsSuperUser])
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
    return Response(group, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    operation_description="View details of a group"
) 
@api_view(['GET'])
@permission_classes([IsSuperUser])
def view(request, *args, **kwargs):
    group = Group.objects.filter(pk=kwargs.get('pk')).values().first()
    if group is None:
        return Response({"error" : "Group does not exist!"}, status = status.HTTP_404_NOT_FOUND)
    return Response(group, status = status.HTTP_200_OK) 


@swagger_auto_schema(
    method='get',
    operation_description="Get group by slug"
) 
@api_view(['GET'])
@permission_classes([])
def get_group_by_slug(request, group_slug):
    logger.info("get_group_by_slug")
    logger.info(group_slug)
    mock = {
        'id': 4,
        'name': 'A Nova Agência Funerária de Tomar',
        'created_by_id': 1,
        'updated_by_id': 1,
        'image':
            'https://app-funeralonline.s3.amazonaws.com/media/entity/A_Nova_Ag%C3%AAncia_Funer%C3%A1ria_De_Tomar.jpg',
        'subTitle':
            'Pretendemos apoiá-lo a dignificar e homenagear o seu ente querido, de forma  única, célere e profissional',
        'description': '''Em tempos de luto, prometemos cuidar de todas as suas necessidades. Prometemos fornecer-lhe serviço profissional e aconselhamento nas horas difíceis.
            Prestamos uma série de serviços que esperamos poder ajudá-lo quando mais necessita. O nosso serviço de repatriamento garante que o defunto regressa ao país de origem para o seu funeral, caso seja esse o seu desejo.

            Temos ligações com consulados, médicos legistas, alta comissariado, linhas aéreas ou marítimas e autoridades legais.

            Prestamos serviço e aconselhamento de cremação.

            Também fornecemos embalsamento e arte restauradora, cujo objectivo é garantir que o corpo resiste à deterioração.

            Também podemos facilitar serviços de exumação. Os nossos serviços incluem uma casa mortuária moderna, veículos bem equipados e uma sala de embalsamento. Prometemos aliviar-lhe o stress e pressão da situação nesta ocasião difícil.

            Ligue-nos a qualquer hora para solicitar um serviço profissional!''',
        'serviceDescription': 'A nossa agência funerária oferece uma variedade de serviços.',
        'services': [
            {
            'title': 'Transporte',
            'image':
                'https://funerariasantacasa24h.com.br/wp-content/uploads/2019/04/2019-04-extra-transporte-de-corpo.jpg',
            },
            {
            'title': 'Flores Naturais',
            'image':
                'https://www.interflora.pt/blog/wp-content/uploads/florista-ramo-1024x640.jpg',
            },
            {
            'title': 'Flores Artificiais',
            'image': 'https://img.fruugo.com/product/0/83/1004975830_max.jpg',
            },
            {
            'title': 'Velas',
            'image':
                'https://www.raquelsilva.pt/wp-content/uploads/2020/07/15_6_led_candles.jpg',
            },
        ],
        'contacts': {
            'email': ['anovaagenciafunerariadetomar@hotmail.com'],
            'phoneNumbers': ['917 599 010', '919 924 048', '913 749 663', '918 741 923 '],
            'fixPhoneNumbers': ['249311012'],
        },
        'locations': [
            {
                'town': 'Tomar',
                'address': 'Avenida Doutor Cândido Madureira, número 100, 2300-531',
                'coords': [39.60216616485415, -8.413803258940865],
            },
            {
                'town': 'Torres Novas',
                'address': 'Castelo de Torres Novas, 2350-758',
                'coords': [39.479529855618146, -8.540568949235606],
            },
        ],
        'deaths': [
            {
                'image':
                    'https://site.funerariadigitaldoc.pt/wp-content/uploads/2024/02/pexels-ksenia-chernaya-8986691-scaled.jpg',
                'name': 'Maria Antunes',
                'date': 'Tomar 24/02/2024',
            },
            {
                'image':
                    'https://site.funerariadigitaldoc.pt/wp-content/uploads/2024/02/pexels-ksenia-chernaya-8986691-scaled.jpg',
                'name': 'Fernando Gomes',
                'date': 'Tomar 18/02/2024',
            },
            {
                'image':
                    'https://site.funerariadigitaldoc.pt/wp-content/uploads/2024/02/pexels-ksenia-chernaya-8986691-scaled.jpg',
                'name': 'Camila Sousa',
                'date': 'Tomar 22/01/2024',
            },
            {
                'image':
                    'https://site.funerariadigitaldoc.pt/wp-content/uploads/2024/02/pexels-ksenia-chernaya-8986691-scaled.jpg',
                'name': 'Lucas Silva',
                'date': 'Tomar 15/01/2024',
            },
        ],
        'qas': [
            {
                'question':
                    'Como posso organizar um serviço funerário para um ente querido?',
                'answer':
                    'Para organizar um serviço funerário, entre em contacto conosco através do nosso número de telefone disponível na secção de contactos do nosso website. Estaremos prontos para orientá-lo em cada passo do processo, desde a escolha do caixão até a coordenação da cerimónia.',
            },
            {
                'question':
                    'Quais são as opções disponíveis para o local de descanso final?',
                'answer':
                    'Oferecemos diversas opções para o local de descanso final, incluindo sepulturas em cemitérios locais, cremação com urnas personalizadas e mausoléus. Podemos discutir as preferências da sua família e ajudá-lo a tomar decisões que melhor atendam às suas necessidades e tradições.',
            },
            {
                'question': 'Vocês fornecem serviços de pré-planeamento funerário?',
                'answer':
                    'Sim, oferecemos serviços de pré-planeamento funerário para aqueles que desejam aliviar o fardo emocional e financeiro para os seus entes queridos. Entre em contacto conosco para discutir as opções disponíveis e personalizar um plano que atenda aos seus desejos e necessidades específicos.',
            },
        ],
    }

    return Response(mock, status = status.HTTP_200_OK) 

@swagger_auto_schema(
    method='post',
    request_body=GroupUpdateSerializer,
    operation_description="Update a Group"
)    
@api_view(['POST'])
@permission_classes([IsSuperUser])
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
@permission_classes([IsSuperUser])
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
@permission_classes([IsAuthenticated])
def list(request, *args, **kwargs):
    if request.user.is_superuser:
        groups = Group.objects.all().values('id','name')
        return Response(groups, status = status.HTTP_200_OK)
    elif request.user.group_user_id:
        groups = Group.objects.filter(id=request.user.group_user_id).values('id','name')
        return Response(groups, status = status.HTTP_200_OK)
    else:
        return Response(groups, status = status.HTTP_403_FORBIDDEN)



