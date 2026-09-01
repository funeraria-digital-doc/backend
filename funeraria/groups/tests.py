from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from groups.models import Group
from groups.serealizers import GroupCreateSerializer


class GroupModelTests(TestCase):

    def test_slug_is_generated_from_name(self):
        group = Group.objects.create(name='Funeraria Central')
        self.assertEqual(group.slug, 'funeraria-central')

    def test_slug_updates_when_name_changes(self):
        group = Group.objects.create(name='Nome Antigo')
        group.name = 'Nome Novo'
        group.save()
        self.assertEqual(group.slug, 'nome-novo')

    def test_name_must_be_unique(self):
        Group.objects.create(name='Repetido')
        with self.assertRaises(Exception):
            Group.objects.create(name='Repetido')

    def test_str_returns_name(self):
        group = Group.objects.create(name='Grupo Teste')
        self.assertEqual(str(group), 'Grupo Teste')


class GroupCreateSerializerTests(TestCase):

    def test_rejects_duplicate_name(self):
        Group.objects.create(name='Ja Existe')
        serializer = GroupCreateSerializer(data={'name': 'Ja Existe'})
        self.assertFalse(serializer.is_valid())


class GroupCreateViewTests(TestCase):

    def test_create_requires_authentication(self):
        client = APIClient()
        response = client.post('/groups/create/', {'name': 'Nova Funeraria'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
