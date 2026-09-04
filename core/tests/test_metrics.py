from django.test import TestCase
from django.urls import reverse


class MetricsTests(TestCase):
    def test_returns_ok_with_counter_names(self):
        response = self.client.get(reverse('metrics'))

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('requests_total', body)
        self.assertIn('matches_total', body)
        self.assertIsInstance(body['requests_total'], int)
        self.assertIsInstance(body['matches_total'], int)

    def test_requests_total_increases_across_requests(self):
        before = self.client.get(reverse('metrics')).json()['requests_total']

        self.client.get(reverse('metrics'))
        after = self.client.get(reverse('metrics')).json()['requests_total']

        self.assertGreater(after, before)
