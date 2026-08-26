from unittest import mock

from django.test import TestCase

from core.helpers.find_match import match_faces


class MatchFacesTests(TestCase):
    @mock.patch('core.helpers.find_match.face_recognition')
    def test_status_true_when_confidence_meets_tolerance(self, mock_face_recognition):
        mock_face_recognition.load_image_file.side_effect = ["image1", "image2"]
        mock_face_recognition.face_encodings.side_effect = [["enc1"], ["enc2"]]
        mock_face_recognition.face_distance.return_value = [0.1]  # confidence = 0.9

        result = match_faces("path1.jpg", "path2.jpg", tolerance=0.6)

        self.assertTrue(result["status"])
        self.assertAlmostEqual(result["confidence"], 0.9)

    @mock.patch('core.helpers.find_match.face_recognition')
    def test_status_false_when_confidence_below_tolerance(self, mock_face_recognition):
        mock_face_recognition.load_image_file.side_effect = ["image1", "image2"]
        mock_face_recognition.face_encodings.side_effect = [["enc1"], ["enc2"]]
        mock_face_recognition.face_distance.return_value = [0.8]  # confidence = 0.2

        result = match_faces("path1.jpg", "path2.jpg", tolerance=0.6)

        self.assertFalse(result["status"])
        self.assertAlmostEqual(result["confidence"], 0.2)

    @mock.patch('core.helpers.find_match.face_recognition')
    def test_no_face_in_new_image_returns_false_status(self, mock_face_recognition):
        mock_face_recognition.load_image_file.side_effect = ["image1", "image2"]
        mock_face_recognition.face_encodings.side_effect = [[], ["enc2"]]

        result = match_faces("path1.jpg", "path2.jpg", tolerance=0.6)

        self.assertFalse(result["status"])
        self.assertEqual(result["confidence"], 0.0)

    @mock.patch('core.helpers.find_match.get_match_tolerance', return_value=0.5)
    @mock.patch('core.helpers.find_match.face_recognition')
    def test_uses_config_tolerance_when_none_given(self, mock_face_recognition, mock_get_tolerance):
        mock_face_recognition.load_image_file.side_effect = ["image1", "image2"]
        mock_face_recognition.face_encodings.side_effect = [["enc1"], ["enc2"]]
        mock_face_recognition.face_distance.return_value = [0.4]  # confidence = 0.6

        result = match_faces("path1.jpg", "path2.jpg")

        mock_get_tolerance.assert_called_once()
        self.assertTrue(result["status"])
