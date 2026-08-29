from django.test import TestCase

from core.models import Citizen, Config, Incident
from core.services_incidents import record_incident


class RecordIncidentTests(TestCase):
    def setUp(self):
        self.driver = Citizen.objects.create(
            first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1",
        )

    def test_saves_incident_against_driver(self):
        result = record_incident(self.driver, {'title': 'Speeding', 'points': 1, 'comment': 'Too fast'})

        self.assertEqual(result['status'], 'saved')
        self.assertEqual(Incident.objects.filter(citizen=self.driver).count(), 1)
        self.assertEqual(result['incident'].citizen, self.driver)

    def test_invalid_form_data_returns_invalid_without_saving(self):
        result = record_incident(self.driver, {'points': 1})  # comment is required

        self.assertEqual(result['status'], 'invalid')
        self.assertEqual(Incident.objects.filter(citizen=self.driver).count(), 0)

    def test_blacklists_driver_once_points_exceed_threshold(self):
        Config.objects.create(maximum_points_threshold=2)

        record_incident(self.driver, {'title': 'A', 'points': 3, 'comment': 'x'})

        self.driver.refresh_from_db()
        self.assertTrue(self.driver.is_blacklisted)
        self.assertEqual(self.driver.blacklist_reason, 'Points Exceeded Limit')

    def test_does_not_blacklist_when_points_within_threshold(self):
        Config.objects.create(maximum_points_threshold=5)

        record_incident(self.driver, {'title': 'A', 'points': 1, 'comment': 'x'})

        self.driver.refresh_from_db()
        self.assertFalse(self.driver.is_blacklisted)
