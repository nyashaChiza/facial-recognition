from core.metrics import increment


def request_counter_middleware(get_response):
    """
    Increments the requests_total metric for every request the app
    handles, regardless of which view served it or what it returned.
    """
    def middleware(request):
        increment('requests_total')
        return get_response(request)

    return middleware
