from django.test import TestCase
from template_logic.models import TemplateLogic


class TemplateLogicModelTests(TestCase):

    def test_str_returns_title(self):
        template = TemplateLogic.objects.create(
            title='Declaracao de obito',
            send_type=['EMAIL'],
            send_email_to=[],
            send_email_to_cc=[],
            send_email_to_bcc=[]
        )
        self.assertEqual(str(template), 'Declaracao de obito')

    def test_validations_default_to_none(self):
        template = TemplateLogic.objects.create(
            title='Outro modelo',
            send_type=[],
            send_email_to=[],
            send_email_to_cc=[],
            send_email_to_bcc=[]
        )
        self.assertIsNone(template.validations)
