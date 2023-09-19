import logging
from template_logic.models import TemplateLogic
from records.models import Record
from django.core.cache import cache
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
import random

logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='get',
    operation_description="get templates per day data"
) 
@api_view(['GET'])
def templates_per_day(request, *args, **kwargs):
    days_number = int(request.query_params.get('days'))
    if days_number is None:
        return Response({'error': 'Dia inválido'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    cache_key = 'templates_created_in_last_' + str(days_number)
    result = cache.get(cache_key)
    if not result:
        logger.info('não tinha cache')
        days_ago = datetime.now() - timedelta(days=days_number)
        pipeline = [
            {
                '$match': {
                    'created_at': {'$gte': days_ago}
                }
            },
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$created_at'
                        }
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$project': {
                    'categories': '$_id',
                    'data': '$count'
                }
            },
            {
                '$sort': {'categories': 1}
            }
        ]

        stats = TemplateLogic.objects.mongo_aggregate(pipeline)    
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days_number)]
        stats_dict = {stat['categories']: stat['data'] for stat in stats}
        for date in dates:
            if date not in stats_dict:
                stats_dict[date] = 0
        result = [{'categories': date, 'data': data} for date, data in stats_dict.items()]

        result.sort(key=lambda x: x['categories'])
        cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response(result, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="get deaths per day data"
) 
@api_view(['GET'])
def deaths_per_day(request, *args, **kwargs):
    days_number = int(request.query_params.get('days'))
    if days_number is None:
        return Response({'error': 'Dia inválido'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    cache_key = 'deaths_in_last_' + str(days_number)
    result = cache.get(cache_key)
    if not result:
        logger.info('não tinha cache')
        days_ago = datetime.now() - timedelta(days=days_number)
        pipeline = [
            {
                '$match': {
                    'death_date': {'$gte': days_ago}
                }
            },
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$death_date'
                        }
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$project': {
                    'categories': '$_id',
                    'data': '$count'
                }
            },
            {
                '$sort': {'categories': 1}
            }
        ]

        stats = Record.objects.mongo_aggregate(pipeline)    
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days_number)]
        stats_dict = {stat['categories']: stat['data'] for stat in stats}
        for date in dates:
            if date not in stats_dict:
                stats_dict[date] = 0
        result = [{'categories': date, 'data': data} for date, data in stats_dict.items()]
        result.sort(key=lambda x: x['categories'])
        cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response(result, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="get deaths by district data"
) 
@api_view(['GET'])
def deaths_by_district(request, *args, **kwargs):
    days_number = int(request.query_params.get('days'))
    if days_number is None:
        return Response({'error': 'Dia inválido'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    cache_key = 'deaths_by_district_in_last_' + str(days_number)
    result = cache.get(cache_key)
    if not result:
        logger.info('não tinha cache')
        days_ago = datetime.now() - timedelta(days=days_number)
        districts = ['Aveiro','Beja','Braga','Bragança','Castelo Branco','Coimbra','Évora','Faro','Guarda','Leiria','Lisboa','Portalegre','Porto','Santarém','Setúbal','Viana do Castelo','Vila Real','Viseu']
        default_data = dict.fromkeys(districts, 0)
        pipeline = [
            {
                '$match': {
                    'wake_date': {'$gte': days_ago}
                }
            },
            {
                '$group': {
                    '_id': '$district',
                    'count': {'$sum': 1}
                }
            },
            {
                '$project': {
                    'district': '$_id',
                    'count': 1,
                    '_id' : 0
                }
            },
            {
                '$sort': {'count': -1}
            }
        ]

        stats = Record.objects.mongo_aggregate(pipeline)  
        api_data = {stat['district']: stat['count'] for stat in stats}
        for key, value in api_data.items():
            default_data[key] = value
        sorted_obj = dict(sorted(default_data.items(), key=lambda item: item[1],reverse=True))
        sum_total = sum(sorted_obj.values())
        top_five = dict(list(sorted_obj.items())[:5])
        sum_top_five = sum(top_five.values())
        others_count = sum_total - sum_top_five
        top_five['Outros'] = others_count
        result = top_five
        cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response(result, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="get deaths by user data"
) 
@api_view(['GET'])
def deaths_by_user(request, *args, **kwargs):
    days_number = int(request.query_params.get('days'))
    if days_number is None:
        return Response({'error': 'Dia inválido'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    cache_key = 'deaths_by_user_in_last_' + str(days_number)
    result = cache.get(cache_key)
    if not result:
        logger.info('não tinha cache')
        days_ago = datetime.now() - timedelta(days=days_number)
        pipeline = [
            {
                '$match': {
                    'wake_date': {'$gte': days_ago}
                }
            },
            {
                '$lookup': {
                    'from': 'accounts_user', 
                    'localField': 'created_by_id',
                    'foreignField': 'id',
                    'as': 'user'
                }
            },
            {
                '$unwind': '$user'
            },
            {
                '$group': {
                    '_id': '$user.username',
                    'count': {'$sum': 1}
                }
            },
            {
                '$project': {
                    'username': '$_id',
                    'count': 1,
                    '_id' : 0
                }
            },
            {
                '$sort': {'count': -1}
            }
        ]

        stats = Record.objects.mongo_aggregate(pipeline)  
        api_data = {stat['username']: stat['count'] for stat in stats}
        result = dict(sorted(api_data.items(), key=lambda item: item[1],reverse=True))
        cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response(result, status = status.HTTP_200_OK)
