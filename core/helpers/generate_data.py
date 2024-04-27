# helpers.py
from faker import Faker
from core.models import Citizen, Incident, CitizenImage
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import random
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

fake = Faker()

def generate_random_data(num_citizens=25, num_incidents_per_citizen=50):
    for _ in range(num_citizens):
        # Generate fake Citizen data
        citizen = Citizen.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            id_type=random.choice(['Passport', 'National ID', 'Driver License']),
            id_number=fake.unique.random_number(digits=10)
        )

        # Generate fake CitizenImage data

        CitizenImage.objects.create(citizen=citizen)
        settings.LOGGER.info(f"Driver created: {citizen}")
        # Generate fake Incident data
        for _ in range(random.randint(0,num_incidents_per_citizen)):
            incident = Incident.objects.create(
                citizen=citizen,
                title=fake.sentence(),
                comment=fake.paragraph(),
                incident_date=timezone.now() - timedelta(days=random.randint(1, 130))
            )
            settings.LOGGER.info(f"Incident created: {incident}")


