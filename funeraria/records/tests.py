from django.test import TestCase
from records.models import Record


class RecordModelTests(TestCase):

    def test_str_returns_name(self):
        record = Record.objects.create(
            name='Maria Silva',
            gender='WOMAN',
            family_member_phone='912345678'
        )
        self.assertEqual(str(record), 'Maria Silva')

    def test_default_status_is_active(self):
        record = Record.objects.create(
            name='Jose Costa',
            gender='MALE',
            family_member_phone='913456789'
        )
        self.assertEqual(record.status, 'ACTIVE')

    def test_name_must_be_unique(self):
        Record.objects.create(name='Ana Pereira', gender='WOMAN', family_member_phone='914567890')
        with self.assertRaises(Exception):
            Record.objects.create(name='Ana Pereira', gender='WOMAN', family_member_phone='915678901')
