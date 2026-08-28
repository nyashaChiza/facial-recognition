import base64
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from core.models import Citizen, Config, Incident

VALID_IMAGE_DATA = 'data:image/png;base64,' + base64.b64encode(b'fake-image-bytes').decode()


class CaptureIncidentBlacklistThresholdTests(TestCase):
    def setUp(self):
        Config.objects.all().delete()
        self.driver = Citizen.objects.create(
            first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1",
        )

    def _post_incident(self, points):
        with mock.patch('core.views_incidents.find_face') as mock_find_face:
            mock_find_face.return_value = {'driver': self.driver, 'score': 0.9, 'status': True}
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


class CaptureIncidentNoMatchTests(TestCase):
    def test_no_face_detected_shows_face_not_detected_message(self):
        with mock.patch('core.views_incidents.find_face', return_value=None):
            response = self.client.post(
                reverse('incident-capture'),
                {'title': 'Speeding', 'comment': 'test', 'points': 1, 'image_data': VALID_IMAGE_DATA},
                follow=True,
            )

        messages = [str(m) for m in response.context['messages']]
        self.assertTrue(any('No face detected' in m for m in messages))
        self.assertEqual(Incident.objects.count(), 0)

    def test_face_detected_but_no_matching_driver_shows_distinct_message(self):
        unmatched_driver = Citizen.objects.create(
            first_name="John", last_name="Roe", id_type="Passport", id_number="X9",
        )
        # status=False: a face was detected, but it didn't clear the match
        # tolerance against this (or any) registered driver.
        no_match_result = {'driver': unmatched_driver, 'score': 0.05, 'status': False}

        with mock.patch('core.views_incidents.find_face', return_value=no_match_result):
            response = self.client.post(
                reverse('incident-capture'),
                {'title': 'Speeding', 'comment': 'test', 'points': 1, 'image_data': VALID_IMAGE_DATA},
                follow=True,
            )

        messages = [str(m) for m in response.context['messages']]
        self.assertTrue(any('does not match any registered driver' in m for m in messages))
        self.assertEqual(Incident.objects.count(), 0)
