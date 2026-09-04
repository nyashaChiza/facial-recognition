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
