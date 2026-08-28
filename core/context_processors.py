from core.models import Config


def nav_config(request):
    """Expose the singleton Config row to every template, so the nav can
    link to System Settings without every view having to pass it in."""
    return {'nav_config': Config.objects.first()}
