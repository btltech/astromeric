import uuid

from starlette.testclient import TestClient

import backend.app.transit_alerts as transit_alerts
from backend.app.main import app
from backend.app.models import Profile, SessionLocal, TransitSubscription


def _profile_payload(name_prefix: str = "Transit Guest") -> dict:
    return {
        "name": f"{name_prefix} {uuid.uuid4().hex[:8]}",
        "date_of_birth": "1992-04-18",
        "time_of_birth": "09:15:00",
        "time_confidence": "exact",
        "place_of_birth": "Lagos, Nigeria",
        "latitude": 6.5244,
        "longitude": 3.3792,
        "timezone": "Africa/Lagos",
        "house_system": "Placidus",
    }


def test_subscribe_transit_alerts_accepts_inline_guest_profile_payload():
    client = TestClient(app)
    email = f"transit-guest-{uuid.uuid4().hex[:8]}@example.com"
    profile_payload = _profile_payload()

    response = client.post(
        "/v2/transits/subscribe",
        json={"email": email, "profile": profile_payload},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["email"] == email
    assert data["subscribed"] is True

    db = SessionLocal()
    try:
        profile = db.query(Profile).filter(Profile.id == data["profile_id"]).first()
        assert profile is not None
        assert profile.user_id is None
        assert profile.name == profile_payload["name"]

        subscriptions = (
            db.query(TransitSubscription)
            .filter(
                TransitSubscription.profile_id == profile.id,
                TransitSubscription.email == email,
            )
            .all()
        )
        assert len(subscriptions) == 1
    finally:
        db.close()


def test_subscribe_transit_alerts_reuses_materialized_guest_profile_and_subscription():
    client = TestClient(app)
    email = f"transit-reuse-{uuid.uuid4().hex[:8]}@example.com"
    profile_payload = _profile_payload(name_prefix="Transit Reuse")

    first = client.post(
        "/v2/transits/subscribe",
        json={"email": email, "profile": profile_payload},
    )
    second = client.post(
        "/v2/transits/subscribe",
        json={"email": email, "profile": profile_payload},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["profile_id"] == second.json()["data"]["profile_id"]

    db = SessionLocal()
    try:
        matching_profiles = (
            db.query(Profile).filter(Profile.name == profile_payload["name"]).all()
        )
        assert len(matching_profiles) == 1

        subscriptions = (
            db.query(TransitSubscription)
            .filter(
                TransitSubscription.profile_id == matching_profiles[0].id,
                TransitSubscription.email == email,
            )
            .all()
        )
        assert len(subscriptions) == 1
    finally:
        db.close()


def test_upcoming_exact_transits_accepts_inline_profile_payload(monkeypatch):
    client = TestClient(app)
    profile_payload = _profile_payload(name_prefix="Exact Transit")
    expected = [
        {
            "transit_planet": "Saturn",
            "natal_point": "Sun",
            "aspect": "trine",
            "exact_date": "2026-04-24T09:30:00+00:00",
            "orb": 0.12,
            "is_applying": True,
            "significance": "major",
            "interpretation": "Steady progress rewards disciplined choices.",
        }
    ]

    monkeypatch.setattr(
        transit_alerts,
        "find_future_exact_transits",
        lambda profile, days_ahead: expected,
    )

    response = client.post(
        "/v2/transits/upcoming-exact?days_ahead=5",
        json={"profile": profile_payload},
    )

    assert response.status_code == 200
    assert response.json()["data"] == expected
