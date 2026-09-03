from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from .models import Citizen

# Below this y-coordinate there's no room left to start another incident
# block (each block below draws up to 7 lines); showPage()+reset once we
# cross it, rather than silently drawing off the bottom of the page.
PAGE_BOTTOM_MARGIN = 100
PAGE_TOP_START = 800


def _safe_report_filename(citizen):
    """
    Build a Content-Disposition-safe filename: strip quotes (header
    injection via a crafted name) and fall back to a slug if the name has
    characters HTTP headers can't carry (headers are latin-1 only, so a
    non-ASCII name would otherwise raise UnicodeEncodeError when the
    response is sent).
    """
    name = f"{citizen.first_name} {citizen.last_name}".replace('"', "'")
    try:
        name.encode('latin-1')
    except UnicodeEncodeError:
        name = slugify(name) or f'driver-{citizen.pk}'
    return f"{name} Report.pdf"


def generate_incident_report(request, citizen_id):
    citizen = get_object_or_404(Citizen, pk=citizen_id)
    incidents = citizen.incidents.all()

    response = HttpResponse(content_type='application/pdf')
    filename = _safe_report_filename(citizen)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Incident Report for {citizen.first_name} {citizen.last_name} ")
    p.drawString(100, 780, f"Is Blacklist : {'Yes' if citizen.is_blacklisted else 'No'} ")
    p.drawString(100, 760, f"ID Type: {citizen.id_type} ")
    p.drawString(100, 740, f"ID Number: {citizen.id_number} ")
    p.drawString(100, 720, f"Total Points: {citizen.get_total_points()} ")

    if citizen.is_blacklisted:
        p.drawString(100, 700, f"Blacklist Reason: {citizen.blacklist_reason} ")
    y_position = 680
    for incident in incidents:
        if y_position < PAGE_BOTTOM_MARGIN:
            p.showPage()
            y_position = PAGE_TOP_START

        y_position -= 20
        p.drawString(100, y_position, f"Title: {incident.title}")
        y_position -= 15
        p.drawString(100, y_position, f"Points: {incident.points}")
        y_position -= 20
        p.drawString(100, y_position, f"Vehicle Reg Number: {incident.vehicle_registration_number}")
        y_position -= 15
        p.drawString(100, y_position, f"Location: {incident.location}")
        y_position -= 15
        p.drawString(100, y_position, f"Comment: {incident.comment}")
        y_position -= 15
        p.drawString(100, y_position, f"Created: {incident.incident_date}")
        y_position -= 15
        p.drawString(100, y_position, "--------------------------------------------")

    p.showPage()
    p.save()

    return response
