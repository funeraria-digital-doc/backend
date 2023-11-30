import logging
from funeraria.permissions import IsAdminOrUpper
from records.models import Record
from django.core.cache import cache
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
from dateutil.relativedelta import relativedelta
logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='get',
    operation_description="get templates per day data"
) 
@api_view(['GET'])
@permission_classes([IsAdminOrUpper])
def deaths_per_months(request, *args, **kwargs):
    months = int(request.query_params.get('months'))
    if months is None:
        return Response({'error': 'Dia inválido'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    cache_key = 'records_per_month_' + str(months)
    result = None
    #cache.get(cache_key)
    if not result:
        now = datetime.now()
        days_before = (now - relativedelta(months=(months-1))).replace(day=1)
        days_after = (now + relativedelta(months=(1))).replace(day=1)
        match_condition = {'death_date': {'$gte': days_before, '$lt': days_after}}
        if request.user.group_user_id is not None:
            match_condition['group_id'] = request.user.group_user_id
        pipeline = [
            {
                '$match': match_condition
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
        stats_dict = {}
        for stat in stats:
            stats_dict[stat['categories']] = stat['data']
        if not stats_dict:
            return Response({}, status = status.HTTP_200_OK)
        for date in dates:
            if date not in stats_dict:
                stats_dict[date] = 0
        result = [{'categories': date, 'data': data} for date, data in stats_dict.items()]

        result.sort(key=lambda x: x['categories'])
        #cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response(result, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="get deaths per day data"
) 
@api_view(['GET'])
@permission_classes([IsAdminOrUpper])
def deaths_per_day(request, *args, **kwargs):
    days_number = int(request.query_params.get('days'))
    if days_number is None:
        return Response({'error': 'Dia inválido'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    cache_key = 'deaths_in_last_' + str(days_number)
    result = None
    #cache.get(cache_key)
    if not result:
        days_before = datetime.now() - timedelta(days=days_number)
        days_after = datetime.now() + timedelta(days=1)
        match_condition = {'death_date': {'$gte': days_before, '$lt': days_after}}
        if request.user.group_user_id is not None:
            match_condition['group_id'] = request.user.group_user_id
        pipeline = [
            {
                '$match': match_condition
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
        if not stats_dict:
            return Response({}, status = status.HTTP_200_OK)
        for date in dates:
            if date not in stats_dict:
                stats_dict[date] = 0
        result = [{'categories': date, 'data': data} for date, data in stats_dict.items()]
        result.sort(key=lambda x: x['categories'])
        #cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response(result, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="get deaths by district data"
) 
@api_view(['GET'])
@permission_classes([IsAdminOrUpper])
def deaths_by_district(request, *args, **kwargs):
    days_number = int(request.query_params.get('days'))
    if days_number is None:
        return Response({'error': 'Dia inválido'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    cache_key = 'deaths_by_district_in_last_' + str(days_number)
    result = None
    #cache.get(cache_key)
    if not result:
        days_before = datetime.now() - timedelta(days=days_number)
        days_after = datetime.now() + timedelta(days=1)
        logger.info('days before - ' + str(days_before))
        logger.info('days after - ' + str(days_after))
        match_condition = {'death_date': {'$gte': days_before, '$lt': days_after}}
        if request.user.group_user_id is not None:
            match_condition['group_id'] = request.user.group_user_id
        districts = ['Aveiro','Beja','Braga','Bragança','Castelo Branco','Coimbra','Évora','Faro','Guarda','Leiria','Lisboa','Portalegre','Porto','Santarém','Setúbal','Viana do Castelo','Vila Real','Viseu']
        default_data = dict.fromkeys(districts, 0)
        logger.info('default_data')
        logger.info(default_data)
        pipeline = [
            {
                '$match': match_condition
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
        logger.info('api_data')
        logger.info(api_data)
        if not api_data:
            return Response({}, status = status.HTTP_200_OK)
        for key, value in api_data.items():
            default_data[key] = value
        logger.info('default_data')
        logger.info(default_data)
        sorted_obj = dict(sorted(default_data.items(), key=lambda item: item[1],reverse=True))
        logger.info('sorted_obj')
        logger.info(sorted_obj)
        sum_total = sum(sorted_obj.values())
        logger.info('sum_total')
        logger.info(sum_total)
        top_five = dict(list(sorted_obj.items())[:5])
        logger.info('top_five')
        logger.info(top_five)
        sum_top_five = sum(top_five.values())
        logger.info('sum_top_five')
        logger.info(sum_top_five)
        others_count = sum_total - sum_top_five
        logger.info('others_count')
        logger.info(others_count)
        top_five['Outros'] = others_count
        logger.info('top_five')
        logger.info(top_five)
        result = top_five
        #cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response(result, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="get deaths by user data"
) 
@api_view(['GET'])
@permission_classes([IsAdminOrUpper])
def deaths_by_user(request, *args, **kwargs):
    days_number = int(request.query_params.get('days'))
    if days_number is None:
        return Response({'error': 'Dia inválido'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    cache_key = 'deaths_by_user_in_last_' + str(days_number)
    result = None
    #cache.get(cache_key)
    if not result:
        days_before = datetime.now() - timedelta(days=days_number)
        days_after = datetime.now() + timedelta(days=1)
        match_condition = {'wake_date': {'$gte': days_before, '$lt': days_after}}
        if request.user.group_user_id is not None:
            match_condition['group_id'] = request.user.group_user_id
        pipeline = [
            {
                '$match': match_condition
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
        api_data = {}
        for stat in stats:
            api_data[stat['username']] = stat['count']
        if not api_data:
            return Response(api_data, status = status.HTTP_200_OK)
        logger.info('api_data')
        logger.info(api_data)
        result = dict(sorted(api_data.items(), key=lambda item: item[1],reverse=True))
        #cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response(result, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="get current month services number"
) 
@api_view(['GET'])
@permission_classes([IsAdminOrUpper])
def current_month_services(request, *args, **kwargs):
    cache_key = 'current_month_services'
    result = None
    #cache.get(cache_key)
    if not result:
        now = datetime.now()
        days_ago = now.replace(day=1)  
        result = Record.objects.filter(death_date__gte=days_ago).count()
        #cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response({'result': result}, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="get current year services number"
) 
@api_view(['GET'])
@permission_classes([IsAdminOrUpper])
def current_year_services(request, *args, **kwargs):
    cache_key = 'current_year_services'
    result = None
    #cache.get(cache_key)
    if not result:
        now = datetime.now()
        days_ago = now.replace(day=1, month=1)  
        result = Record.objects.filter(death_date__gte=days_ago).count()
        #cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response({'result': result}, status = status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="get best month"
) 
@api_view(['GET'])
@permission_classes([IsAdminOrUpper])
def best_month(request, *args, **kwargs):
    cache_key = 'best_month'
    result = None
    #cache.get(cache_key)
    if not result:
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
        #cache.set(cache_key, result)
    else:
        cache.touch(cache_key)
    return Response({'result': result}, status = status.HTTP_200_OK)