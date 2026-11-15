
from fastapi import HTTPException

from app.services import user_service


def test_create_user(
    client, monkeypatch, valid_user, saved_user
):
    monkeypatch.setattr(
        user_service,
        "create_user",
        lambda user: saved_user
    )

    response = client.post(
        "/users/",
        json=valid_user
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["email"] == valid_user["email"]


def test_create_user_missing_email(client, valid_user):
    del valid_user["email"]

    response = client.post(
        "/users/",
        json=valid_user
    )

    assert response.status_code == 422


def test_create_user_invalid_email(client, valid_user):
    valid_user["email"] = "invalid"

    response = client.post(
        "/users/",
        json=valid_user
    )

    assert response.status_code == 422


def test_get_user(client, monkeypatch, saved_user):
    monkeypatch.setattr(
        user_service,
        "get_user",
        lambda user_id: saved_user
    )

    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_user_not_found(client, monkeypatch):
    def fake_get(user_id):
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    monkeypatch.setattr(
        user_service,
        "get_user",
        fake_get
    )

    response = client.get("/users/999")

    assert response.status_code == 404


def test_update_user(client, monkeypatch, saved_user):
    monkeypatch.setattr(
        user_service,
        "update_user",
        lambda user_id, user: {
            **saved_user,
            "email": "new@example.com"
        }
    )

    response = client.patch(
        "/users/1",
        json={"email": "new@example.com"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "new@example.com"


def test_delete_user(client, monkeypatch):
    monkeypatch.setattr(
        user_service,
        "delete_user",
        lambda user_id: {"id": user_id}
    )

    response = client.delete("/users/1")

    assert response.status_code == 204


def test_invalid_user_id(client):
    response = client.get("/users/not-a-number")

    assert response.status_code == 422


def test_password_hash_not_exposed(
    client, monkeypatch, saved_user
):
    monkeypatch.setattr(
        user_service,
        "get_user",
        lambda user_id: saved_user
    )

    response = client.get("/users/1")

    assert response.status_code == 200
    assert "password_hash" not in response.json()

