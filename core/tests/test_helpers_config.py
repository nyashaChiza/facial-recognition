from django.test import TestCase

from core.models import Config
from core.helpers.face_recon import get_face_match_threshold, DEFAULT_FACE_MATCH_THRESHOLD
from core.helpers.find_match import get_match_tolerance, DEFAULT_MATCH_TOLERANCE


class GetFaceMatchThresholdTests(TestCase):
    def test_falls_back_to_default_when_no_config_row_exists(self):
        Config.objects.all().delete()
        self.assertEqual(get_face_match_threshold(), DEFAULT_FACE_MATCH_THRESHOLD)

    def test_uses_config_row_when_one_exists(self):
        Config.objects.all().delete()
        Config.objects.create(minimum_detection_threshold=42)
        self.assertEqual(get_face_match_threshold(), 42)


class GetMatchToleranceTests(TestCase):
    def test_falls_back_to_default_when_no_config_row_exists(self):
        Config.objects.all().delete()
        self.assertEqual(get_match_tolerance(), DEFAULT_MATCH_TOLERANCE)

    def test_uses_config_row_when_one_exists(self):
        Config.objects.all().delete()
        Config.objects.create(maximum_detection_threshold=77)
        self.assertEqual(get_match_tolerance(), 77)
