"""/v2/geocode/timezone: the IANA zone for a birthplace (no network in tests)."""

from starlette.testclient import TestClient

from backend.app import geocode_service
from backend.app.main import app
from backend.app.routers import geocode

client = TestClient(app)


def _clear():
    geocode._cache.clear()


def test_returns_the_looked_up_zone_and_caches_it(monkeypatch):
    _clear()
    calls = []

    def fake(lat, lon):
        calls.append((lat, lon))
        return "Africa/Lagos"

    monkeypatch.setattr(geocode, "fetch_iana_timezone", fake)
    for _ in range(2):
        resp = client.get("/v2/geocode/timezone", params={"lat": 6.4541, "lon": 3.3947})
        assert resp.status_code == 200
        assert resp.json()["timezone"] == "Africa/Lagos"
        assert resp.json()["estimated"] is False
    assert calls == [(6.45, 3.39)]


def test_estimates_without_caching_when_the_lookup_fails(monkeypatch):
    _clear()
    monkeypatch.setattr(geocode, "fetch_iana_timezone", lambda lat, lon: None)
    data = client.get("/v2/geocode/timezone", params={"lat": 6.45, "lon": 3.39}).json()
    # East of Greenwich is UTC+, which Etc/GMT writes with a minus sign.
    assert data == {
        "latitude": 6.45,
        "longitude": 3.39,
        "timezone": "UTC",
        "estimated": True,
    }
    data = client.get("/v2/geocode/timezone", params={"lat": 35.7, "lon": 139.7}).json()
    assert data["timezone"] == "Etc/GMT-9"
    assert geocode._cache == {}


def test_rejects_impossible_coordinates():
    assert (
        client.get("/v2/geocode/timezone", params={"lat": 95, "lon": 0}).status_code
        == 422
    )


def test_fetch_returns_none_on_a_bad_answer(monkeypatch):
    class Resp:
        status_code = 200

        @staticmethod
        def json():
            return {"timeZone": ""}

    class Client:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, url):
            return Resp()

    monkeypatch.setattr(geocode_service.httpx, "Client", Client)
    assert geocode_service.fetch_iana_timezone(6.45, 3.39) is None
