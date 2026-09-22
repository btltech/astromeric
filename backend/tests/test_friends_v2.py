import json
import warnings

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.models import Base, Friend
from backend.app.routers import friends as friends_router

warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)

# Friend owner keys must be unguessable per-install secrets (UUID / 32+ hex).
OWNER_A = "3f2b8c1e-7d4a-4e5b-9c6d-0a1b2c3d4e5f"
OWNER_B = "9a8b7c6d-5e4f-4a3b-8c2d-1e0f9a8b7c6d"
OWNER_C = "c0ffee00c0ffee00c0ffee00c0ffee00"


@pytest.fixture(autouse=True)
def isolated_friends_db(monkeypatch, tmp_path):
    db_path = tmp_path / "friends.sqlite"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(friends_router, "SessionLocal", testing_session)
    monkeypatch.setattr(
        friends_router, "_STORE_PATH", tmp_path / "legacy_friends_store.json"
    )

    yield testing_session

    engine.dispose()


def test_compare_all_friends_uses_owner_profile_and_owner_id(isolated_friends_db):
    friend_payload = {
        "owner_id": OWNER_A,
        "friend": {
            "id": "friend-1",
            "name": "Test Partner",
            "date_of_birth": "1992-09-03",
            "relationship_type": "friendship",
            "avatar_emoji": "✨",
        },
    }
    add_resp = client.post("/v2/friends/add", json=friend_payload)
    assert add_resp.status_code == 200

    with isolated_friends_db() as db:
        rows = db.query(Friend).filter(Friend.owner_id == OWNER_A).all()
        assert len(rows) == 1
        assert rows[0].friend_id == "friend-1"

    compare_all_payload = {
        "owner_id": OWNER_A,
        "owner_profile": {
            "name": "Test User",
            "date_of_birth": "1990-06-15",
            "time_of_birth": "14:30:00",
            "time_confidence": "exact",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York",
        },
    }
    compare_all_resp = client.post("/v2/friends/compare-all", json=compare_all_payload)
    assert compare_all_resp.status_code == 200

    body = compare_all_resp.json()
    assert body["status"] == "success"
    assert len(body["data"]) == 1
    assert body["data"][0]["friend_id"] == "friend-1"


def test_compare_with_friend_migrates_legacy_store(isolated_friends_db):
    legacy_store = {
        OWNER_B: [
            {
                "id": "friend-2",
                "name": "Stored Friend",
                "date_of_birth": "1991-01-20",
                "relationship_type": "friendship",
            }
        ]
    }
    friends_router._STORE_PATH.write_text(json.dumps(legacy_store))

    compare_payload = {
        "owner_id": OWNER_B,
        "friend_id": "friend-2",
        "relationship_type": "friendship",
        "owner_profile": {
            "name": "Owner",
            "date_of_birth": "1990-06-15",
            "time_of_birth": "14:30:00",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York",
        },
    }
    compare_resp = client.post("/v2/friends/compare", json=compare_payload)
    assert compare_resp.status_code == 200

    body = compare_resp.json()["data"]
    assert body["friend_id"] == "friend-2"
    assert body["friend_name"] == "Stored Friend"

    with isolated_friends_db() as db:
        row = (
            db.query(Friend)
            .filter(Friend.owner_id == OWNER_B, Friend.friend_id == "friend-2")
            .first()
        )
        assert row is not None


def test_add_friend_logs_do_not_include_raw_name(caplog):
    payload = {
        "owner_id": OWNER_C,
        "friend": {
            "id": "friend-privacy",
            "name": "Privacy Test Friend",
            "date_of_birth": "1993-11-04",
            "relationship_type": "friendship",
        },
    }

    with caplog.at_level("INFO", logger="backend.app.routers.friends"):
        response = client.post("/v2/friends/add", json=payload)

    assert response.status_code == 200
    assert "Privacy Test Friend" not in caplog.text
    assert "Friend added" in caplog.text


GUESSABLE_OWNERS = ["-1", "-2", "0", "1", "42", "privacy-owner", "", "abc123"]


@pytest.mark.parametrize("owner", [o for o in GUESSABLE_OWNERS if o])
def test_list_rejects_guessable_owner_ids(owner):
    resp = client.get(f"/v2/friends/list/{owner}")
    assert resp.status_code == 403
    assert resp.json()["detail"]["code"] == "FRIENDS_OWNER_KEY_REQUIRED"


@pytest.mark.parametrize("owner", GUESSABLE_OWNERS)
def test_add_rejects_guessable_owner_ids_and_stores_nothing(owner, isolated_friends_db):
    resp = client.post(
        "/v2/friends/add",
        json={
            "owner_id": owner,
            "friend": {"id": "f-1", "name": "Someone", "date_of_birth": "1990-01-01"},
        },
    )
    assert resp.status_code == 403
    with isolated_friends_db() as db:
        assert db.query(Friend).count() == 0


def test_remove_compare_and_compare_all_reject_guessable_owner_ids():
    assert client.delete("/v2/friends/remove/-1/f-1").status_code == 403
    assert (
        client.post(
            "/v2/friends/compare",
            json={
                "owner_id": "-1",
                "friend_id": "f-1",
                "owner_profile": {"name": "Me", "date_of_birth": "1990-01-01"},
            },
        ).status_code
        == 403
    )
    resp = client.post(
        "/v2/friends/compare-all",
        json={
            "owner_id": "-1",
            "owner_profile": {"name": "Me", "date_of_birth": "1990-01-01"},
        },
    )
    assert resp.status_code == 403


def test_existing_rows_under_shared_owner_ids_are_unreachable(isolated_friends_db):
    """Rows written before containment under a shared id (e.g. "-1") stay stored
    but can no longer be read through the API."""
    with isolated_friends_db() as db:
        db.add(
            Friend(
                owner_id="-1",
                friend_id="legacy-friend",
                name="Another user's friend",
                date_of_birth="1970-01-01",
            )
        )
        db.commit()
    assert client.get("/v2/friends/list/-1").status_code == 403


def test_owner_keys_are_isolated():
    for owner, name in ((OWNER_A, "Friend of A"), (OWNER_B, "Friend of B")):
        assert (
            client.post(
                "/v2/friends/add",
                json={
                    "owner_id": owner,
                    "friend": {
                        "id": "same-id",
                        "name": name,
                        "date_of_birth": "1990-01-01",
                    },
                },
            ).status_code
            == 200
        )
    names_a = [
        f["name"] for f in client.get(f"/v2/friends/list/{OWNER_A}").json()["data"]
    ]
    names_b = [
        f["name"] for f in client.get(f"/v2/friends/list/{OWNER_B}").json()["data"]
    ]
    assert names_a == ["Friend of A"]
    assert names_b == ["Friend of B"]
