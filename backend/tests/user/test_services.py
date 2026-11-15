
import pytest
from fastapi import HTTPException

from app.models.user import UserCreate, UserUpdate
from app.services import user_service


def test_create_user(monkeypatch, valid_user, saved_user):
    monkeypatch.setattr(
        user_service.user_repository,
        "get_user_by_email",
        lambda email: None
    )

    monkeypatch.setattr(
        user_service.user_repository,
        "create_user",
        lambda email, password_hash: saved_user
    )

    result = user_service.create_user(
        UserCreate(**valid_user)
    )

    assert result["id"] == 1


def test_get_user(monkeypatch, saved_user):
    monkeypatch.setattr(
        user_service.user_repository,
        "get_user_by_id",
        lambda user_id: saved_user
    )

    result = user_service.get_user(1)

    assert result["email"] == "test@example.com"


def test_get_user_not_found(monkeypatch):
    monkeypatch.setattr(
        user_service.user_repository,
        "get_user_by_id",
        lambda user_id: None
    )

    with pytest.raises(HTTPException) as error:
        user_service.get_user(999)

    assert error.value.status_code == 404


def test_update_user(monkeypatch, saved_user):
    monkeypatch.setattr(
        user_service.user_repository,
        "get_user_by_email",
        lambda email: None
    )

    monkeypatch.setattr(
        user_service.user_repository,
        "update_user",
        lambda user_id, email, password_hash: {
            **saved_user,
            "email": "new@example.com"
        }
    )

    result = user_service.update_user(
        1,
        UserUpdate(email="new@example.com")
    )

    assert result["email"] == "new@example.com"


def test_update_user_not_found(monkeypatch):
    monkeypatch.setattr(
        user_service.user_repository,
        "get_user_by_email",
        lambda email: None
    )

    monkeypatch.setattr(
        user_service.user_repository,
        "update_user",
        lambda user_id, email, password_hash: None
    )

    with pytest.raises(HTTPException) as error:
        user_service.update_user(
            999,
            UserUpdate(email="new@example.com")
        )

    assert error.value.status_code == 404


def test_delete_user(monkeypatch):
    monkeypatch.setattr(
        user_service.user_repository,
        "delete_user",
        lambda user_id: {"id": user_id}
    )

    result = user_service.delete_user(1)

    assert result == {"id": 1}


def test_delete_user_not_found(monkeypatch):
    monkeypatch.setattr(
        user_service.user_repository,
        "delete_user",
        lambda user_id: None
    )

    with pytest.raises(HTTPException) as error:
        user_service.delete_user(999)

    assert error.value.status_code == 404
