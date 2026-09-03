from django.test import TestCase

from core.validators import (
    PayloadValidationError,
    validate_blacklist_payload,
    validate_capture_payload,
    validate_citizen_payload,
)


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


class ValidateBlacklistPayloadTests(TestCase):
    def test_missing_blacklist_reason_raises(self):
        with self.assertRaises(PayloadValidationError):
            validate_blacklist_payload({})

    def test_non_string_blacklist_reason_raises(self):
        with self.assertRaises(PayloadValidationError):
            validate_blacklist_payload({'blacklist_reason': ['not', 'a', 'string']})

    def test_valid_payload_does_not_raise(self):
        validate_blacklist_payload({'blacklist_reason': 'Repeated violations'})


class ValidateCitizenPayloadTests(TestCase):
    def test_missing_required_field_raises(self):
        with self.assertRaises(PayloadValidationError):
            validate_citizen_payload({'first_name': 'Jane', 'last_name': 'Doe', 'id_type': 'Passport'})

    def test_non_string_field_raises(self):
        with self.assertRaises(PayloadValidationError):
            validate_citizen_payload({
                'first_name': ['Jane'], 'last_name': 'Doe', 'id_type': 'Passport', 'id_number': 'X1',
            })

    def test_valid_payload_does_not_raise(self):
        validate_citizen_payload({
            'first_name': 'Jane', 'last_name': 'Doe', 'id_type': 'Passport', 'id_number': 'X1',
        })
