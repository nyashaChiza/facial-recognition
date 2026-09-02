from django.test import TestCase

from core.models import Citizen, Incident, CitizenImage, Config


class CitizenModelTests(TestCase):
    def setUp(self):
        self.citizen = Citizen.objects.create(
            first_name="Jane",
            last_name="Doe",
            id_type="Passport",
            id_number="AB123456",
        )

    def test_str_returns_full_name(self):
        self.assertEqual(str(self.citizen), "Jane Doe")

    def test_get_total_points_with_no_incidents_is_zero(self):
        self.assertEqual(self.citizen.get_total_points(), 0)

    def test_get_total_points_sums_incident_points(self):
        Incident.objects.create(citizen=self.citizen, comment="Speeding", points=3)
        Incident.objects.create(citizen=self.citizen, comment="Parking", points=2)

        self.assertEqual(self.citizen.get_total_points(), 5)


class IncidentModelTests(TestCase):
    def test_str_returns_citizen_full_name(self):
        citizen = Citizen.objects.create(
            first_name="John",
            last_name="Smith",
            id_type="National ID",
            id_number="ID987654",
        )
        incident = Incident.objects.create(citizen=citizen, comment="Late night stop")

        self.assertEqual(str(incident), "John Smith")
        self.assertEqual(incident.points, 1)  # model default


class CitizenImageModelTests(TestCase):
    def test_str_returns_citizen_full_name(self):
        citizen = Citizen.objects.create(
            first_name="Amy",
            last_name="Lee",
            id_type="Driver License",
            id_number="DL555",
        )
        image = CitizenImage.objects.create(citizen=citizen, image="citizen/images/test.jpg")

        self.assertEqual(str(image), "Amy Lee")


class ConfigDefaultRowTests(TestCase):
    def test_migration_seeds_exactly_one_config_row_with_model_defaults(self):
        # core/migrations/0006_seed_default_config.py creates this row so the
        # app has a usable Config immediately after a fresh `migrate`, since
        # the config-update form has no way to create the first one (it
        # requires an existing pk). 0007 then fixes maximum_detection_threshold's
        # default (99 made no sense as a percentage-based cosine tolerance).
        self.assertEqual(Config.objects.count(), 1)

        config = Config.objects.first()
        assert config is not None
        self.assertEqual(config.minimum_detection_threshold, 1)
        self.assertEqual(config.maximum_detection_threshold, 40)
        self.assertEqual(config.maximum_points_threshold, 1)
