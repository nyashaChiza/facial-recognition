from django.http import JsonResponse

from core.metrics import get_counters


def metrics(request):
    return JsonResponse(get_counters())
