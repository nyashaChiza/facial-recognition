from unittest import mock

from django.test import TestCase
from django.urls import reverse

from core.models import Citizen


class CitizenListViewTests(TestCase):
    def test_renders_with_no_citizens(self):
        response = self.client.get(reverse('citizen-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['citizens']), [])

    def test_renders_with_citizens(self):
        Citizen.objects.create(first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1")
        response = self.client.get(reverse('citizen-list'))
        self.assertEqual(len(response.context['citizens']), 1)


class BlacklistedCitizenListViewTests(TestCase):
    def test_only_shows_blacklisted_citizens(self):
        Citizen.objects.create(
            first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1", is_blacklisted=False
        )
        blacklisted = Citizen.objects.create(
            first_name="John", last_name="Roe", id_type="Passport", id_number="X2", is_blacklisted=True
        )
        response = self.client.get(reverse('blacklist'))
        self.assertEqual(list(response.context['citizens']), [blacklisted])


class SearchCitizensTests(TestCase):
    def test_search_matches_by_name(self):
        Citizen.objects.create(first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1")
        Citizen.objects.create(first_name="John", last_name="Roe", id_type="Passport", id_number="X2")

        response = self.client.get(reverse('search_citizens'), {'search_query': 'Doe'})

        self.assertEqual(len(response.context['citizens']), 1)
        self.assertEqual(response.context['citizens'][0].last_name, 'Doe')

    def test_empty_query_returns_no_results(self):
        Citizen.objects.create(first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1")
        response = self.client.get(reverse('search_citizens'))
        self.assertEqual(response.context['citizens'], [])

    def test_comma_separated_query_matches_multiple_drivers(self):
        jane = Citizen.objects.create(first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1")
        john = Citizen.objects.create(first_name="John", last_name="Roe", id_type="Passport", id_number="X2")
        Citizen.objects.create(first_name="Mary", last_name="Sue", id_type="Passport", id_number="X3")

        response = self.client.get(reverse('search_citizens'), {'search_query': 'Doe, Roe'})

        self.assertEqual(set(response.context['citizens']), {jane, john})

    def test_comma_separated_query_does_not_duplicate_matches(self):
        jane = Citizen.objects.create(first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1")

        response = self.client.get(reverse('search_citizens'), {'search_query': 'Jane, Doe'})

        self.assertEqual(list(response.context['citizens']), [jane])


class BlacklistCitizenViewTests(TestCase):
    def test_post_blacklists_citizen_and_redirects(self):
        citizen = Citizen.objects.create(first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1")

        response = self.client.post(
            reverse('blacklist-driver', args=[citizen.id]),
            {'is_blacklisted': True, 'blacklist_reason': 'Repeated violations'},
        )

        citizen.refresh_from_db()
        self.assertTrue(citizen.is_blacklisted)
        self.assertEqual(citizen.blacklist_reason, 'Repeated violations')
        self.assertRedirects(response, reverse('citizen-detail', kwargs={'pk': citizen.id}))

    def test_404_for_missing_citizen(self):
        response = self.client.get(reverse('blacklist-driver', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_missing_blacklist_reason_key_redirects_without_saving(self):
        citizen = Citizen.objects.create(first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1")

        response = self.client.post(reverse('blacklist-driver', args=[citizen.id]), {'is_blacklisted': True})

        citizen.refresh_from_db()
        self.assertFalse(citizen.is_blacklisted)
        self.assertRedirects(response, reverse('citizen-detail', kwargs={'pk': citizen.id}))


class ReinstateCitizenViewTests(TestCase):
    def test_post_reinstates_citizen(self):
        citizen = Citizen.objects.create(
            first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1",
            is_blacklisted=True, blacklist_reason="Old reason",
        )

        response = self.client.post(reverse('reinstate-driver', args=[citizen.id]))

        citizen.refresh_from_db()
        self.assertFalse(citizen.is_blacklisted)
        self.assertEqual(citizen.blacklist_reason, "")
        self.assertRedirects(response, reverse('citizen-list'))

    def test_get_is_not_allowed_and_does_not_mutate(self):
        citizen = Citizen.objects.create(
            first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1",
            is_blacklisted=True, blacklist_reason="Old reason",
        )

        response = self.client.get(reverse('reinstate-driver', args=[citizen.id]))

        self.assertEqual(response.status_code, 405)
        citizen.refresh_from_db()
        self.assertTrue(citizen.is_blacklisted)

    def test_404_for_missing_citizen(self):
        response = self.client.post(reverse('reinstate-driver', args=[999]))
        self.assertEqual(response.status_code, 404)


class CaptureDriverViewTests(TestCase):
    @mock.patch('core.services.find_face')
    def test_saves_new_driver_when_no_duplicate_found(self, mock_find_face):
        mock_find_face.return_value = None

        response = self.client.post(
            reverse('driver-create'),
            {
                'first_name': 'Jane', 'last_name': 'Doe',
                'id_type': 'Passport', 'id_number': 'X1',
                'image_data': 'data:image/png;base64,ZmFrZQ==',
            },
        )

        self.assertRedirects(response, reverse('citizen-list'))
        self.assertTrue(Citizen.objects.filter(id_number='X1').exists())

    @mock.patch('core.services.find_face')
    def test_warns_without_saving_when_duplicate_found(self, mock_find_face):
        existing = Citizen.objects.create(first_name="John", last_name="Roe", id_type="Passport", id_number="X2")
        mock_find_face.return_value = {'status': True, 'driver': existing, 'score': 0.9}

        response = self.client.post(
            reverse('driver-create'),
            {
                'first_name': 'Jane', 'last_name': 'Doe',
                'id_type': 'Passport', 'id_number': 'X1',
                'image_data': 'data:image/png;base64,ZmFrZQ==',
            },
        )

        self.assertRedirects(response, reverse('citizen-list'))
        self.assertFalse(Citizen.objects.filter(id_number='X1').exists())

    def test_missing_image_data_does_not_crash(self):
        response = self.client.post(
            reverse('driver-create'),
            {'first_name': 'Jane', 'last_name': 'Doe', 'id_type': 'Passport', 'id_number': 'X1'},
        )

        self.assertRedirects(response, reverse('citizen-list'))
        self.assertFalse(Citizen.objects.filter(id_number='X1').exists())


class EditCitizenViewTests(TestCase):
    def setUp(self):
        self.citizen = Citizen.objects.create(
            first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1",
        )

    def test_get_renders_form_prefilled_with_existing_values(self):
        response = self.client.get(reverse('citizen-update', args=[self.citizen.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance, self.citizen)

    def test_post_updates_fields_without_touching_photo(self):
        response = self.client.post(
            reverse('citizen-update', args=[self.citizen.pk]),
            {'first_name': 'Janet', 'last_name': 'Doe', 'id_type': 'Passport', 'id_number': 'X1'},
        )

        self.assertRedirects(response, reverse('citizen-detail', kwargs={'pk': self.citizen.pk}))
        self.citizen.refresh_from_db()
        self.assertEqual(self.citizen.first_name, 'Janet')

    def test_post_with_image_data_updates_photo(self):
        response = self.client.post(
            reverse('citizen-update', args=[self.citizen.pk]),
            {
                'first_name': 'Jane', 'last_name': 'Doe', 'id_type': 'Passport', 'id_number': 'X1',
                'image_data': 'data:image/png;base64,ZmFrZQ==',
            },
        )

        self.assertRedirects(response, reverse('citizen-detail', kwargs={'pk': self.citizen.pk}))
        self.citizen.refresh_from_db()
        self.assertTrue(self.citizen.picture.name)

    def test_invalid_form_does_not_save(self):
        response = self.client.post(
            reverse('citizen-update', args=[self.citizen.pk]),
            {'first_name': '', 'last_name': 'Doe', 'id_type': 'Passport', 'id_number': 'X1'},
        )

        self.assertEqual(response.status_code, 200)
        self.citizen.refresh_from_db()
        self.assertEqual(self.citizen.first_name, 'Jane')

    def test_missing_required_key_redirects_without_saving(self):
        # id_number is entirely absent, not just blank - a malformed
        # request rather than a normal validation error a user would hit
        # through the form itself.
        response = self.client.post(
            reverse('citizen-update', args=[self.citizen.pk]),
            {'first_name': 'Janet', 'last_name': 'Doe', 'id_type': 'Passport'},
        )

        self.assertRedirects(response, reverse('citizen-detail', kwargs={'pk': self.citizen.pk}))
        self.citizen.refresh_from_db()
        self.assertEqual(self.citizen.first_name, 'Jane')
