from django.test import TestCase

from core.models import Config
from core.helpers.face_recon import face_confidence, get_face_match_threshold, DEFAULT_FACE_MATCH_THRESHOLD
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


class FaceConfidenceTests(TestCase):
    def test_above_threshold_returns_percentage_string(self):
        result = face_confidence(face_distance=0.8, face_match_threshold=0.6)
        self.assertEqual(result, "25.0%")

    def test_at_or_below_threshold_returns_below_threshold_message(self):
        result = face_confidence(face_distance=0.3, face_match_threshold=0.6)
        self.assertEqual(result, "confidence below threshold")

    def test_falls_back_to_config_threshold_when_none_given(self):
        Config.objects.all().delete()
        Config.objects.create(minimum_detection_threshold=0)

        result = face_confidence(face_distance=0.5)

        self.assertEqual(result, "25.0%")
