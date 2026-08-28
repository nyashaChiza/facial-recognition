from unittest import mock

from django.test import TestCase

from core.helpers.find_match import match_faces


class MatchFacesTests(TestCase):
    @mock.patch('core.helpers.find_match._get_recognizer')
    @mock.patch('core.helpers.find_match._detect_and_extract_feature')
    def test_status_true_when_confidence_meets_tolerance(self, mock_detect, mock_get_recognizer):
        mock_detect.side_effect = ['feature1', 'feature2']
        mock_get_recognizer.return_value.match.return_value = 0.9

        result = match_faces("path1.jpg", "path2.jpg", tolerance=0.6)

        self.assertTrue(result["status"])
        self.assertAlmostEqual(result["confidence"], 0.9)

    @mock.patch('core.helpers.find_match._get_recognizer')
    @mock.patch('core.helpers.find_match._detect_and_extract_feature')
    def test_status_false_when_confidence_below_tolerance(self, mock_detect, mock_get_recognizer):
        mock_detect.side_effect = ['feature1', 'feature2']
        mock_get_recognizer.return_value.match.return_value = 0.2

        result = match_faces("path1.jpg", "path2.jpg", tolerance=0.6)

        self.assertFalse(result["status"])
        self.assertAlmostEqual(result["confidence"], 0.2)

    @mock.patch('core.helpers.find_match._detect_and_extract_feature')
    def test_no_face_in_new_image_returns_false_status(self, mock_detect):
        mock_detect.return_value = None

        result = match_faces("path1.jpg", "path2.jpg", tolerance=0.6)

        self.assertFalse(result["status"])
        self.assertEqual(result["confidence"], 0.0)
        self.assertIn("new image", result["message"])

    @mock.patch('core.helpers.find_match._detect_and_extract_feature')
    def test_no_face_in_existing_image_returns_false_status(self, mock_detect):
        mock_detect.side_effect = ['feature1', None]

        result = match_faces("path1.jpg", "path2.jpg", tolerance=0.6)

        self.assertFalse(result["status"])
        self.assertEqual(result["confidence"], 0.0)
        self.assertIn("existing image", result["message"])

    @mock.patch('core.helpers.find_match.get_match_tolerance', return_value=0.5)
    @mock.patch('core.helpers.find_match._get_recognizer')
    @mock.patch('core.helpers.find_match._detect_and_extract_feature')
    def test_uses_config_tolerance_when_none_given(self, mock_detect, mock_get_recognizer, mock_get_tolerance):
        mock_detect.side_effect = ['feature1', 'feature2']
        mock_get_recognizer.return_value.match.return_value = 0.6

        result = match_faces("path1.jpg", "path2.jpg")

        mock_get_tolerance.assert_called_once()
        self.assertTrue(result["status"])
