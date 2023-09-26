import random
from django.shortcuts import render

# Create your views here.
from faker import Faker
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.test import APIClient
from records.serealizers import RecordCreateSerializer
from groups.serealizers import GroupCreateSerializer
from groups.models import Group
from accounts.models import User
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
def create_record(request):
    quantity = request.data.get('quantity') if request.data.get('quantity') else 1
    fake = Faker(['pt_PT'])
    final_result = {
        'success' : [],
        'error' : [],
    }
    while quantity > 0:
        gender = fake.random_element(elements=('WOMAN', 'MALE'))
        age = fake.random_int(min=18, max=90)
        death_date = (datetime.now() - timedelta(days=(random.randint(1, 80))))
        random_hour = random.randint(10, 16)
        random_minute = random.choice([0, 30])
        wake_time = death_date + timedelta(hours=random_hour, minutes=random_minute)
        group = request.data.get('group') if request.data.get('group') is not None else fake.random_element(elements=Group.objects.all().values('id')).get('id')
        users_from_group = []
        users_ids = User.objects.filter(group_user_id = int(group)).values('id')
        for userId in users_ids:
            users_from_group.append(userId.get('id'))
        created_by = random.choice(users_from_group) if len(users_from_group) > 0 else None
        client = APIClient()
        logger.info('created_by ' + (str(created_by) if created_by is not None else 'none'))
        if created_by is not None:
            user = User.objects.filter(id=created_by).first()
            if user is not None:
                client.force_authenticate(user=user)
            else:
                client.force_authenticate()
        else:
            client.force_authenticate()
            continue
            
        record_data = {
            "group": group,
            "email": fake.unique.email(),
            "status": 'ACTIVE',
            "name": fake.name_female() if gender == 'WOMAN' else fake.name_male(),
            "gender": str(gender),
            "marital_status": fake.random_element(elements=('SINGLE', 'MARIED', 'DIVORCED', 'WIDOWER')),
            "cc": fake.random_number(digits=9),
            "nif": str(fake.bothify(text='##########??#')),
            "niss": fake.random_number(digits=10),
            "birthday": (datetime.now() - timedelta(days= (365*age) - (random.randint(10,300)))).strftime('%Y-%m-%d'),
            "age": age,
            "address": fake.address(),
            "parish": fake.freguesia(),
            "municipality": fake.concelho(),
            "district": fake.distrito(),
            "nationality": "Portuguesa",
            "mother_name": fake.name_female(),
            "father_name": fake.name_male(),
            "last_mariage_date": str(fake.date_this_century()),
            "spouse_name": fake.name_male() if gender == 'WOMAN' else fake.name_female(),
            "spouse_gender": 'MALE' if gender == 'WOMAN' else 'WOMAN',
            "spouse_age": round(age * (random.randint(9, 11) / 10)),
            "naturality_parish": fake.freguesia(),
            "naturality_municipality": fake.concelho(),
            "death_date": death_date.strftime('%Y-%m-%d'),
            "death_time": str(fake.time()),
            "death_address": fake.address(),
            "death_parish": fake.freguesia(),
            "death_municipality": fake.concelho(),
            "cemetery": fake.word(),
            "cemetery_municipality": fake.concelho(),
            "grave_number": str(fake.random_number(digits=3)),
            "grave_row": str(fake.random_number(digits=3)),
            "grave_site": str(fake.random_number(digits=3)),
            "death_retired": fake.boolean(chance_of_getting_true=50),
            "death_left_assets": fake.boolean(chance_of_getting_true=50),
            "death_made_will": fake.boolean(chance_of_getting_true=50),
            "death_leaves_hereditary": fake.boolean(chance_of_getting_true=50),
            "double_head_address" :fake.address(),
            "flowers" :fake.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None),
            "dead_location" :fake.address(),
            "cause_of_death" :fake.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None),
            "grave_message" :fake.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None),
            "wake_local" :fake.address(),
            "wake_date" : (death_date + timedelta(days=2)).strftime('%Y-%m-%d'),
            "wake_time" :wake_time.strftime('%H:%M:%S'),
            "leaving_mortuary_datetime" :(wake_time + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            "funeral_datetime" :(wake_time + timedelta(days=2) + timedelta(hours= 4)).time().strftime('%Y-%m-%d %H:%M:%S'),
            "funeral_local" :fake.address(),
            "family_member_name" :fake.name(), 
            "family_member_cc" :str(fake.random_number(digits=9)), 
            "family_member_cc_valid_until" :(death_date + timedelta(days=365)).strftime('%Y-%m-%d'), 
            "family_member_kinship" :fake.word(), 
            "family_member_phone" :str(fake.phone_number()), 
            "death_declaration_number" :str(fake.random_number(digits=10))
        }

        serializer = RecordCreateSerializer(data=record_data)
        if serializer.is_valid():
            try:
                if created_by is not None and user is not None:
                    logger.info('save with user - ' + user.username + " - " + record_data.get('name'))
                    serializer.save(created_by=user, updated_by=user)
                    final_result.get('success').append(serializer.data)
                else:
                    logger.info('save no user')
                    final_result.get('error').append({'data': 'no user'}) 
                    quantity = quantity + 1               
            except Exception as e:
                logger.info('save error')
                logger.info(e)
                final_result.get('error').append({'data': serializer.data})
        else:
            logger.info('error')
            final_result.get('error').append(serializer.errors)
        quantity = quantity - 1
            
    return Response({'success' : True, 'data': final_result}, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_group_with_users(request):
    staff = request.data.get('staff') if request.data.get('staff') is not None else 1
    users = request.data.get('users') if request.data.get('users') is not None else 3
    fake = Faker(['pt_PT'])
    created_users = {
        'staff' : [],
        'users' : []
    }
    group_id = None
    try:
        payload = {
            'name': 'Funerária ' + str(fake.last_name())
        }
        serializer = GroupCreateSerializer(data= payload)
        if serializer.is_valid():
            serializer.save()
            group = Group.objects.filter(name = serializer.data.get('name')).first()
            group_id = group.id
            counter_staff_errors = 0
            while staff > 0 and counter_staff_errors < 10:
                logger.info('Creating staff user')
                name = str(fake.user_name())
                try:
                    user = User.objects.create_user(
                        username=name,
                        password='12345678',
                        email= name + '@example.com',
                        group_user = group,
                        is_staff=True
                    )
                    created_users.get('staff').append(user.id)
                    logger.info('Staff User created - ' + user.username)
                    staff = staff - 1
                except Exception as e:
                    logger.info(e)
                    counter_staff_errors = counter_staff_errors + 1
                    logger.info('Error Creating staff user')
            counter_users_errors = 0
            while users > 0 and counter_users_errors < 10:
                logger.info('Creating user')
                name = str(fake.user_name())
                try:
                    user = User.objects.create_user(
                        username=name,
                        password='12345678',
                        email= name + '@example.com',
                        group_user = group
                    )
                    created_users.get('users').append(user.id)
                    users = users - 1
                    logger.info('User created - ' + user.username)
                except Exception as e:
                    logger.info(e)
                    counter_users_errors = counter_users_errors + 1
                    logger.info('Error Creating user')
                
        else:
            logger.info('Group not valid')
    except Exception as e:
        logger.info(e)
        return Response({'success' : False, 'data': 'group not created'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if len(created_users.get('staff')) != (request.data.get('staff') if request.data.get('staff') is not None else 1) or len(created_users.get('users')) != (request.data.get('users') if request.data.get('users') is not None else 3):
        for i in range(len(created_users.get('staff'))):
            User.objects.filter(id=created_users.get('staff')[i]).delete()
            created_users.get('staff').pop(i)
        for o in range(len(created_users.get('users'))):
            User.objects.filter(id=created_users.get('users')[o]).delete()
            created_users.get('users').pop(o)
        if group_id is not None:
            Group.objects.filter(id = group_id).first().delete()
    return Response({'success' : True, 'data': created_users}, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_templates(request):
    from django.core.cache import caches

    cache = caches['default']  # Replace 'default' with your cache alias, if needed
    keys_values = cache._cache


    # for key, value in keys_values.items():
    #     print(f"Key: {key}, Value: {value}")

    return Response({'success' : True, 'data': keys_values}, status=status.HTTP_200_OK)