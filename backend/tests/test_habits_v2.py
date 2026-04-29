import warnings

from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.routers import habits as habits_router

# Suppress the deprecation warning - TestClient still works fine
warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)


def test_v2_habits_log_entry_accepts_int_habit_id():
    # Ensure a clean in-memory store for deterministic ids
    habits_router._HABITS.clear()
    habits_router._ENTRIES.clear()

    create_payload = {
        "name": "Drink water",
        "category": "health",
        "frequency": "daily",
        "description": "",
    }
    resp = client.post("/v2/habits/create", json=create_payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    habit_id_str = body["data"]["id"]
    assert habit_id_str.isdigit()

    # iOS sends `habit_id` as an Int; accept it.
    log_payload = {"habit_id": int(habit_id_str), "completed": True, "note": None}
    resp = client.post("/v2/habits/log-entry", json=log_payload)
    assert resp.status_code == 200
    log_body = resp.json()
    assert log_body["status"] == "success"
    assert log_body["data"]["completed"] is True
