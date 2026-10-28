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
    assert sleeps == [0.1]


def test_fetch_caps_persistent_disconnect_at_three_attempts(monkeypatch):
    calls = []

    def opener(request, timeout):
        calls.append(request.full_url)
        raise URLError(RemoteDisconnected("sentinel connection detail"))

    monkeypatch.setattr(check_services, "urlopen", opener)
    monkeypatch.setattr(check_services.time, "sleep", lambda _: None)

    with pytest.raises(RuntimeError, match="after 3 attempts") as error:
        check_services.fetch("http://127.0.0.1:24686/api/services")
    assert len(calls) == 3
    assert "sentinel connection detail" not in str(error.value)


def test_fetch_does_not_retry_http_status_errors(monkeypatch):
    calls = []

    def opener(request, timeout):
        calls.append(request.full_url)
        raise HTTPError(request.full_url, 503, "unavailable", None, None)

    monkeypatch.setattr(check_services, "urlopen", opener)

    with pytest.raises(RuntimeError, match="HTTP 503"):
        check_services.fetch("http://127.0.0.1:24686/api/services")
    assert len(calls) == 1
