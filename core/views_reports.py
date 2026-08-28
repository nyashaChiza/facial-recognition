from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Citizen


def generate_incident_report(request, citizen_id):
    citizen = get_object_or_404(Citizen, pk=citizen_id)
    incidents = citizen.incidents.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{citizen.first_name} {citizen.last_name} Report.pdf"'

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
