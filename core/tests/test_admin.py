from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from core.admin import ConfigAdmin
from core.models import Config


class ConfigAdminSingletonTests(TestCase):
    def setUp(self):
        self.admin = ConfigAdmin(Config, AdminSite())

    def test_add_is_allowed_when_no_config_row_exists(self):
        Config.objects.all().delete()

        self.assertTrue(self.admin.has_add_permission(request=None))

    def test_add_is_blocked_once_a_config_row_exists(self):
        Config.objects.create()

        self.assertFalse(self.admin.has_add_permission(request=None))
