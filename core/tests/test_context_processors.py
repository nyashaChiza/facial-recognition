from django.test import TestCase
from django.urls import reverse

from core.models import Config


class NavConfigContextProcessorTests(TestCase):
    def test_exposes_the_config_row_to_every_page(self):
        response = self.client.get(reverse('citizen-list'))
        self.assertEqual(response.context['nav_config'], Config.objects.first())

    def test_none_when_no_config_row_exists(self):
        Config.objects.all().delete()
        response = self.client.get(reverse('citizen-list'))
        self.assertIsNone(response.context['nav_config'])
