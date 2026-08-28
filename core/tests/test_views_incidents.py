import base64
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from core.models import Citizen, Config

VALID_IMAGE_DATA = 'data:image/png;base64,' + base64.b64encode(b'fake-image-bytes').decode()


class CaptureIncidentBlacklistThresholdTests(TestCase):
    def setUp(self):
        Config.objects.all().delete()
        self.driver = Citizen.objects.create(
            first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1",
        )

    def _post_incident(self, points):
        with mock.patch('core.views_incidents.find_face') as mock_find_face:
            mock_find_face.return_value = {'driver': self.driver}
            return self.client.post(
                reverse('incident-capture'),
                {
                    'title': 'Speeding', 'comment': 'Caught on camera',
                    'points': points, 'image_data': VALID_IMAGE_DATA,
                },
            )

    def test_blacklists_driver_once_points_exceed_threshold(self):
        Config.objects.create(maximum_points_threshold=5)

        self._post_incident(points=10)

        self.driver.refresh_from_db()
        self.assertTrue(self.driver.is_blacklisted)
        self.assertEqual(self.driver.blacklist_reason, 'Points Exceeded Limit')

    def test_does_not_blacklist_driver_under_threshold(self):
        Config.objects.create(maximum_points_threshold=5)

        self._post_incident(points=2)

        self.driver.refresh_from_db()
        self.assertFalse(self.driver.is_blacklisted)

    def test_uses_model_default_threshold_when_no_config_row_exists(self):
        # Config.objects.all().delete() in setUp leaves no row; the view
        # falls back to 1 (Config.maximum_points_threshold's model default).
        self.assertFalse(Config.objects.exists())

        self._post_incident(points=5)

        self.driver.refresh_from_db()
        self.assertTrue(self.driver.is_blacklisted)
