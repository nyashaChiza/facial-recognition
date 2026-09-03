from unittest import mock

from django.db.utils import OperationalError
from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_returns_ok_status_and_json_body(self):
        response = self.client.get(reverse('health-check'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json(), {'status': 'ok'})


class ReadinessCheckTests(TestCase):
    def test_readiness_checks_db_connection(self):
        response = self.client.get(reverse('readiness-check'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json(), {'status': 'ok', 'checks': {'database': 'ok'}})

    @mock.patch('core.views_health.Citizen.objects.exists')
    def test_returns_503_when_the_database_is_unreachable(self, mock_exists):
        mock_exists.side_effect = OperationalError('unable to open database file')

        response = self.client.get(reverse('readiness-check'))

        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertEqual(body['status'], 'error')
        self.assertIn('unable to open database file', body['checks']['database'])
