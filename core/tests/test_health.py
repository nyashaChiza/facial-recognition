from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_returns_ok_status_and_json_body(self):
        response = self.client.get(reverse('health-check'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json(), {'status': 'ok'})
