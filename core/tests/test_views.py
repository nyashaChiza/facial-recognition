import io
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from pypdf import PdfReader

from core.models import Citizen, Config, Incident


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


class CaptureIncidentViewTests(TestCase):
    @mock.patch('core.views_incidents.find_face')
    def test_no_face_detected_redirects_back_with_warning(self, mock_find_face):
        mock_find_face.return_value = None

        response = self.client.post(
            reverse('incident-capture'),
            {'image_data': 'data:image/png;base64,ZmFrZQ==', 'comment': 'test'},
        )

        self.assertEqual(response.status_code, 302)
        mock_find_face.assert_called_once()

    def test_missing_image_data_redirects_with_warning_instead_of_crashing(self):
        response = self.client.post(reverse('incident-capture'), {'comment': 'test'})

        self.assertRedirects(response, reverse('incident-list'))


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


class GenerateIncidentReportTests(TestCase):
    def test_returns_pdf_for_existing_citizen(self):
        citizen = Citizen.objects.create(first_name="Jane", last_name="Doe", id_type="Passport", id_number="X1")

        response = self.client.get(reverse('generate_incident_report', args=[citizen.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('Jane Doe Report.pdf', response['Content-Disposition'])

    def test_404_for_missing_citizen(self):
        response = self.client.get(reverse('generate_incident_report', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_quote_in_name_does_not_break_content_disposition_header(self):
        citizen = Citizen.objects.create(
            first_name='Jane "JJ"', last_name='Doe', id_type='Passport', id_number='X2',
        )

        response = self.client.get(reverse('generate_incident_report', args=[citizen.id]))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('"JJ"', response['Content-Disposition'])

    def test_non_ascii_name_falls_back_to_a_slug_instead_of_crashing(self):
        citizen = Citizen.objects.create(
            first_name='José', last_name='Müller', id_type='Passport', id_number='X3',
        )

        response = self.client.get(reverse('generate_incident_report', args=[citizen.id]))

        self.assertEqual(response.status_code, 200)
        response['Content-Disposition'].encode('latin-1')  # would raise if non-ASCII leaked through

    def test_paginates_instead_of_running_off_the_page_for_many_incidents(self):
        citizen = Citizen.objects.create(first_name="Busy", last_name="Driver", id_type="Passport", id_number="X4")
        for i in range(10):
            Incident.objects.create(citizen=citizen, title=f"Incident {i}", comment="test")

        response = self.client.get(reverse('generate_incident_report', args=[citizen.id]))

        reader = PdfReader(io.BytesIO(response.content))
        self.assertGreater(len(reader.pages), 1)
