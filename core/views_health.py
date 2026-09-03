from django.db.utils import OperationalError
from django.http import JsonResponse

from .models import Citizen


def health_check(request):
    return JsonResponse({'status': 'ok'})


def readiness_check(request):
    """
    health_check only confirms the process is up; this confirms the app can
    actually reach its database, so an orchestrator/load balancer can tell
    "alive" apart from "ready to serve traffic".
    """
    try:
        Citizen.objects.exists()
    except OperationalError as e:
        return JsonResponse({'status': 'error', 'checks': {'database': str(e)}}, status=503)

    return JsonResponse({'status': 'ok', 'checks': {'database': 'ok'}})
