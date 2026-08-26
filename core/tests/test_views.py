from unittest import mock

from django.test import TestCase
from django.urls import reverse

from core.models import Citizen, Config


class IndexViewTests(TestCase):
    def setUp(self):
        Config.objects.create()

    def test_home_renders_successfully(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_context_includes_search_form_and_config(self):
        response = self.client.get(reverse('home'))
        self.assertIn('search_form', response.context)
        self.assertIsNotNone(response.context['config'])


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


class ReinstateCitizenViewTests(TestCase):
    def test_get_reinstates_citizen(self):
        citizen = Citizen.objects.create(
            first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1",
            is_blacklisted=True, blacklist_reason="Old reason",
        )

        response = self.client.get(reverse('reinstate-driver', args=[citizen.id]))

        citizen.refresh_from_db()
        self.assertFalse(citizen.is_blacklisted)
        self.assertEqual(citizen.blacklist_reason, "")
        self.assertRedirects(response, reverse('citizen-list'))


class CaptureIncidentViewTests(TestCase):
    @mock.patch('core.views.find_face')
    def test_no_face_detected_redirects_back_with_warning(self, mock_find_face):
        mock_find_face.return_value = None

        response = self.client.post(
            reverse('incident-capture'),
            {'image_data': 'data:image/png;base64,ZmFrZQ==', 'comment': 'test'},
        )

        self.assertEqual(response.status_code, 302)
        mock_find_face.assert_called_once()
