import logging
from template_logic.models import TemplateLogic
from records.models import Record
from django.core.cache import cache
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='get',
    operation_description="get templates per day data"
) 
@api_view(['GET'])
def deaths_per_months(request, *args, **kwargs):
    months = int(request.query_params.get('months'))
    if months is None:
        return Response({'error': 'Dia inválido'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    cache_key = 'records_per_month_' + str(months)
    result = cache.get(cache_key)
    if not result:
        logger.info('não tinha cache')
        now = datetime.now()
        days_ago = (now - relativedelta(months=(months-1))).replace(day=1)
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
                            'format': '%Y-%m',
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
        dates = [(datetime.now() - relativedelta(months=(i))).replace(day=1).strftime('%Y-%m') for i in range(months)]
        stats_dict = {stat['categories']: stat['data'] for stat in stats}
        for date in dates:
            if date not in stats_dict:
                stats_dict[date] = 0
        
        result = [{'categories': date, 'data': data} for date, data in stats_dict.items()]

        result.sort(key=lambda x: x['categories'])
        logger.info(result)
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

@swagger_auto_schema(
    method='get',
    operation_description="get current month services number"
) 
@api_view(['GET'])
def current_month_services(request, *args, **kwargs):
    cache_key = 'current_month_services'
    result = cache.get(cache_key)
    if not result:
        logger.info('não tinha cache')
        now = datetime.now()
        days_ago = now.replace(day=1)  
        result = Record.objects.filter(death_date__gte=days_ago).count()
        logger.info(result)
        cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response({'result': result}, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="get current year services number"
) 
@api_view(['GET'])
def current_year_services(request, *args, **kwargs):
    cache_key = 'current_year_services'
    result = cache.get(cache_key)
    if not result:
        logger.info('não tinha cache')
        now = datetime.now()
        days_ago = now.replace(day=1, month=1)  
        result = Record.objects.filter(death_date__gte=days_ago).count()
        logger.info(result)
        cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response({'result': result}, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="get best month"
) 
@api_view(['GET'])
def best_month(request, *args, **kwargs):
    cache_key = 'best_month'
    result = cache.get(cache_key)
    if not result:
        logger.info('não tinha cache')
        days_ago = datetime.now().replace(day=1, month=1)
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
                            'format': '%m',
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
        stats_dict = {}
        for stat in stats:
            stats_dict[stat.get('categories')] = stat.get('data')
        month = max(stats_dict, key=stats_dict.get)
        month_names = {
            '01': 'Janeiro',
            '02': 'Fevereiro',
            '03': 'Março',
            '04': 'Abril',
            '05': 'Maio',
            '06': 'Junho',
            '07': 'Julho',
            '08': 'Agosto',
            '09': 'Setembro',
            '10': 'Outubro',
            '11': 'Novembro',
            '12': 'Dezembro'
        }
        result = month_names.get(month)
        cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response({'result': result}, status = status.HTTP_200_OK)