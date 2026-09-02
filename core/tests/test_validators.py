from django.test import TestCase

from core.validators import PayloadValidationError, validate_capture_payload


class ValidateCapturePayloadTests(TestCase):
    def test_missing_image_data_key_raises(self):
        with self.assertRaises(PayloadValidationError):
            validate_capture_payload({})

    def test_non_string_image_data_raises(self):
        with self.assertRaises(PayloadValidationError):
            validate_capture_payload({'image_data': ['not', 'a', 'string']})

    def test_valid_string_image_data_is_returned(self):
        result = validate_capture_payload({'image_data': 'data:image/png;base64,abc'})

        self.assertEqual(result, 'data:image/png;base64,abc')
