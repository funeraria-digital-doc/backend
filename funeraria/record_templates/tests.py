from django.test import TestCase
from record_templates.models import RecordTemplates
from records.models import Record


class RecordTemplatesModelTests(TestCase):

    def setUp(self):
        self.record = Record.objects.create(
            name='Carlos Mendes',
            gender='MALE',
            family_member_phone='916789012'
        )

    def test_answers_are_saved_as_json(self):
        rt = RecordTemplates.objects.create(
            record=self.record,
            answers={'campo1': 'valor1', 'campo2': 2}
        )
        self.assertEqual(rt.answers.get('campo1'), 'valor1')

    def test_record_template_can_have_no_template(self):
        rt = RecordTemplates.objects.create(record=self.record, template=None, answers={})
        self.assertIsNone(rt.template)
