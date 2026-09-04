import threading

_lock = threading.Lock()
_counters = {
    'requests_total': 0,
    'matches_total': 0,
}


def increment(name: str, amount: int = 1) -> None:
    with _lock:
        _counters[name] = _counters.get(name, 0) + amount


def get_counters() -> dict:
    with _lock:
        return dict(_counters)
