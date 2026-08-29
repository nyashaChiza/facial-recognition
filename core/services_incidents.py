from loguru import logger

from core.forms import IncidentForm
from core.models import Config


def record_incident(driver, form_data):
    """
    Validate and save an incident against `driver`, then re-evaluate their
    blacklist status against the configured points threshold.

    Returns {'status': 'saved', 'incident': Incident} on success, or
    {'status': 'invalid', 'form': IncidentForm} if form_data didn't validate -
    the form is returned so callers can surface its errors.
    """
    incident_form = IncidentForm(form_data)
    if not incident_form.is_valid():
        return {'status': 'invalid', 'form': incident_form}

    incident = incident_form.save(commit=False)
    incident.citizen = driver
    incident.save()

    config = Config.objects.first()
    max_points = config.maximum_points_threshold if config else 1
    if driver.get_total_points() > max_points:
        driver.is_blacklisted = True
        driver.blacklist_reason = 'Points Exceeded Limit'
        driver.save()

    logger.info('Incident recorded for {} (total points now {})', driver, driver.get_total_points())

    return {'status': 'saved', 'incident': incident}
