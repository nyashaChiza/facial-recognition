import base64
from unittest import mock

from django.test import TestCase

from core.models import Citizen
from core.services import (
    InvalidImageDataError,
    decode_captured_image,
    process_driver_capture,
    reinstate_driver,
    update_driver_photo,
    MAX_IMAGE_BYTES,
)

VALID_IMAGE_DATA = 'data:image/png;base64,' + base64.b64encode(b'fake-image-bytes').decode()


class DecodeCapturedImageTests(TestCase):
    def test_decodes_valid_data_url(self):
        ext, decoded = decode_captured_image(VALID_IMAGE_DATA)
        self.assertEqual(ext, 'png')
        self.assertEqual(decoded, b'fake-image-bytes')

    def test_missing_image_data_raises(self):
        with self.assertRaises(InvalidImageDataError):
            decode_captured_image(None)

    def test_empty_string_raises(self):
        with self.assertRaises(InvalidImageDataError):
            decode_captured_image('')

    def test_missing_data_url_prefix_raises(self):
        with self.assertRaises(InvalidImageDataError):
            decode_captured_image(base64.b64encode(b'not-a-data-url').decode())

    def test_missing_base64_marker_raises(self):
        with self.assertRaises(InvalidImageDataError):
            decode_captured_image('data:image/png,notbase64')

    def test_oversized_image_raises(self):
        huge_payload = base64.b64encode(b'x' * (MAX_IMAGE_BYTES + 1)).decode()
        with self.assertRaises(InvalidImageDataError):
            decode_captured_image(f'data:image/png;base64,{huge_payload}')


class ProcessDriverCaptureTests(TestCase):
    def setUp(self):
        self.citizen = Citizen(first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1")

    @mock.patch('core.services.find_face')
    def test_saves_citizen_when_no_duplicate_found(self, mock_find_face):
        mock_find_face.return_value = None

        result = process_driver_capture(self.citizen, VALID_IMAGE_DATA)

        self.assertEqual(result['status'], 'saved')
        self.citizen.refresh_from_db()
        self.assertTrue(self.citizen.picture.name)

    @mock.patch('core.services.find_face')
    def test_reports_duplicate_without_saving(self, mock_find_face):
        existing = Citizen.objects.create(first_name="John", last_name="Roe", id_type="Passport", id_number="X2")
        mock_find_face.return_value = {'status': True, 'driver': existing, 'score': 0.9}

        result = process_driver_capture(self.citizen, VALID_IMAGE_DATA)

        self.assertEqual(result['status'], 'duplicate')
        self.assertEqual(result['detection']['driver'], existing)
        self.assertFalse(Citizen.objects.filter(id_number="X1").exists())

    def test_invalid_image_data_raises_before_calling_find_face(self):
        with self.assertRaises(InvalidImageDataError):
            process_driver_capture(self.citizen, None)


class UpdateDriverPhotoTests(TestCase):
    def test_replaces_the_citizens_photo(self):
        citizen = Citizen.objects.create(first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1")

        result = update_driver_photo(citizen, VALID_IMAGE_DATA)

        self.assertEqual(result.id, citizen.id)
        citizen.refresh_from_db()
        self.assertTrue(citizen.picture.name)

    def test_invalid_image_data_raises(self):
        citizen = Citizen.objects.create(first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1")

        with self.assertRaises(InvalidImageDataError):
            update_driver_photo(citizen, None)


class ReinstateDriverTests(TestCase):
    def test_reinstate_driver_clears_blacklist_flag(self):
        citizen = Citizen.objects.create(
            first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1",
            is_blacklisted=True, blacklist_reason="Points Exceeded Limit",
        )

        result = reinstate_driver(citizen.id)

        self.assertEqual(result.id, citizen.id)
        citizen.refresh_from_db()
        self.assertFalse(citizen.is_blacklisted)
        self.assertEqual(citizen.blacklist_reason, "")
