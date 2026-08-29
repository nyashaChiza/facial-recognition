from django.test import TestCase

from core.forms import BlacklistForm, IncidentForm


class BlacklistFormTests(TestCase):
    def test_empty_reason_is_invalid(self):
        form = BlacklistForm(data={'is_blacklisted': True, 'blacklist_reason': '   '})

        self.assertFalse(form.is_valid())
        self.assertIn('blacklist_reason', form.errors)

    def test_non_empty_reason_is_valid(self):
        form = BlacklistForm(data={'is_blacklisted': True, 'blacklist_reason': 'Repeated violations'})

        self.assertTrue(form.is_valid())


class IncidentFormTests(TestCase):
    def test_malformed_registration_number_is_invalid(self):
        form = IncidentForm(data={'points': 1, 'comment': 'x', 'vehicle_registration_number': 'ABC/123!!'})

        self.assertFalse(form.is_valid())
        self.assertIn('vehicle_registration_number', form.errors)

    def test_valid_registration_number_is_accepted(self):
        form = IncidentForm(data={'points': 1, 'comment': 'x', 'vehicle_registration_number': 'ABC 123-Z'})

        self.assertTrue(form.is_valid())

    def test_blank_registration_number_is_allowed(self):
        form = IncidentForm(data={'points': 1, 'comment': 'x', 'vehicle_registration_number': ''})

        self.assertTrue(form.is_valid())
