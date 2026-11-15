
from fastapi import HTTPException

from app.services import user_profile_service


def test_create_profile(
    client, monkeypatch, valid_profile, saved_profile
):
    monkeypatch.setattr(
        user_profile_service,
        "create_user_profile",
        lambda profile: saved_profile
    )

    response = client.post(
        "/user-profiles/",
        json=valid_profile
    )

    assert response.status_code == 201
    assert response.json()["id"] == 10


def test_create_invalid_height(client, valid_profile):
    valid_profile["height_cm"] = -10

    response = client.post(
        "/user-profiles/",
        json=valid_profile
    )

    assert response.status_code == 422


def test_create_invalid_activity(client, valid_profile):
    valid_profile["activity_level"] = "invalid"

    response = client.post(
        "/user-profiles/",
        json=valid_profile
    )

    assert response.status_code == 422


def test_create_missing_user(client, valid_profile):
    del valid_profile["user_id"]

    response = client.post(
        "/user-profiles/",
        json=valid_profile
    )

    assert response.status_code == 422


def test_get_profile(client, monkeypatch, saved_profile):
    monkeypatch.setattr(
        user_profile_service,
        "get_user_profile",
        lambda user_id: saved_profile
    )

    response = client.get("/user-profiles/1")

    assert response.status_code == 200
    assert response.json()["display_name"] == "Test User"


def test_get_profile_not_found(client, monkeypatch):
    def fake_get(user_id):
        raise HTTPException(
            status_code=404,
            detail="User profile not found"
        )

    monkeypatch.setattr(
        user_profile_service,
        "get_user_profile",
        fake_get
    )

    response = client.get("/user-profiles/999")

    assert response.status_code == 404


def test_update_profile(
    client, monkeypatch, saved_profile
):
    monkeypatch.setattr(
        user_profile_service,
        "update_user_profile",
        lambda user_id, data: {
            **saved_profile,
            "weight_kg": 80
        }
    )

    response = client.patch(
        "/user-profiles/1",
        json={"weight_kg": 80}
    )

    assert response.status_code == 200
    assert float(response.json()["weight_kg"]) == 80


def test_update_invalid_weight(client):
    response = client.patch(
        "/user-profiles/1",
        json={"weight_kg": -5}
    )

    assert response.status_code == 422


def test_delete_profile(client, monkeypatch):
    monkeypatch.setattr(
        user_profile_service,
        "delete_user_profile",
        lambda user_id: {"id": 10}
    )

    response = client.delete("/user-profiles/1")

    assert response.status_code == 204


def test_invalid_user_id(client):
    response = client.get(
        "/user-profiles/not-a-number"
    )

    assert response.status_code == 422

