from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class ErrorTrackingTests(TestCase):
    def test_sentry_dsn_defaults_to_empty_and_is_a_noop(self):
        self.assertEqual(settings.SENTRY_DSN, '')

    def test_app_boots_and_serves_requests_with_sentry_dsn_unset(self):
        response = self.client.get(reverse('health-check'))

        self.assertEqual(response.status_code, 200)
