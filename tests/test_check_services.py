from http.client import RemoteDisconnected
from urllib.error import HTTPError, URLError

import pytest

import scripts.check_services as check_services


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return b'{"data":[]}'


@pytest.mark.parametrize(
    "disconnect",
    [RemoteDisconnected("closed"), URLError(RemoteDisconnected("closed"))],
)
def test_fetch_retries_transient_disconnect_once(monkeypatch, disconnect):
    calls = []
    sleeps = []

    def opener(request, timeout):
        calls.append((request.full_url, timeout))
        if len(calls) == 1:
            raise disconnect
        return FakeResponse()

    monkeypatch.setattr(check_services, "urlopen", opener)
    monkeypatch.setattr(check_services.time, "sleep", sleeps.append)

    assert check_services.fetch("http://127.0.0.1:24686/api/services") == {"data": []}
    assert len(calls) == 2
    assert sleeps == [0.25]


def test_fetch_caps_persistent_disconnect_at_five_attempts_without_trace_id(monkeypatch):
    calls = []
    sleeps = []

    def opener(request, timeout):
        calls.append(request.full_url)
        raise URLError(RemoteDisconnected("sentinel connection detail"))

    monkeypatch.setattr(check_services, "urlopen", opener)
    monkeypatch.setattr(check_services.time, "sleep", sleeps.append)
    trace_id = "0123456789abcdef0123456789abcdef"

    with pytest.raises(RuntimeError, match="jaeger.trace after 5 attempts") as error:
        check_services.fetch(f"http://127.0.0.1:24686/api/traces/{trace_id}")
    assert len(calls) == 5
    assert sleeps == [0.25, 0.5, 1.0, 2.0]
    assert "sentinel connection detail" not in str(error.value)
    assert trace_id not in str(error.value)


def test_fetch_does_not_retry_http_status_errors(monkeypatch):
    calls = []

    def opener(request, timeout):
        calls.append(request.full_url)
        raise HTTPError(request.full_url, 503, "unavailable", None, None)

    monkeypatch.setattr(check_services, "urlopen", opener)

    trace_id = "fedcba9876543210fedcba9876543210"
    with pytest.raises(RuntimeError, match="HTTP 503 from jaeger.trace") as error:
        check_services.fetch(f"http://127.0.0.1:24686/api/traces/{trace_id}")
    assert len(calls) == 1
    assert trace_id not in str(error.value)
