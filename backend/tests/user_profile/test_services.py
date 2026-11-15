
import pytest
from fastapi import HTTPException

from app.models.user_profile import (
    UserProfileCreate,
    UserProfileUpdate
)
from app.services import user_profile_service


def test_create_profile(monkeypatch, valid_profile, saved_profile):
    monkeypatch.setattr(
        user_profile_service.user_repository,
        "get_user_by_id",
        lambda user_id: {"id": user_id}
    )
    monkeypatch.setattr(
        user_profile_service.user_profile_repository,
        "get_profile_by_user_id",
        lambda user_id: None
    )
    monkeypatch.setattr(
        user_profile_service.user_profile_repository,
        "create_profile",
        lambda profile: saved_profile
    )

    result = user_profile_service.create_profile(
        UserProfileCreate(**valid_profile)
    )

    assert result["id"] == 10


def test_create_profile_user_not_found(monkeypatch, valid_profile):
    monkeypatch.setattr(
        user_profile_service.user_repository,
        "get_user_by_id",
        lambda user_id: None
    )

    with pytest.raises(HTTPException) as error:
        user_profile_service.create_profile(
            UserProfileCreate(**valid_profile)
        )

    assert error.value.status_code == 404


def test_create_duplicate_profile(monkeypatch, valid_profile, saved_profile):
    monkeypatch.setattr(
        user_profile_service.user_repository,
        "get_user_by_id",
        lambda user_id: {"id": user_id}
    )
    monkeypatch.setattr(
        user_profile_service.user_profile_repository,
        "get_profile_by_user_id",
        lambda user_id: saved_profile
    )

    with pytest.raises(HTTPException) as error:
        user_profile_service.create_profile(
            UserProfileCreate(**valid_profile)
        )

    assert error.value.status_code == 409


def test_get_profile(monkeypatch, saved_profile):
    monkeypatch.setattr(
        user_profile_service.user_profile_repository,
        "get_profile_by_user_id",
        lambda user_id: saved_profile
    )

    result = user_profile_service.get_profile(1)

    assert result["display_name"] == "Test User"


def test_get_profile_not_found(monkeypatch):
    monkeypatch.setattr(
        user_profile_service.user_profile_repository,
        "get_profile_by_user_id",
        lambda user_id: None
    )

    with pytest.raises(HTTPException) as error:
        user_profile_service.get_profile(999)

    assert error.value.status_code == 404


def test_update_profile(monkeypatch, saved_profile):
    monkeypatch.setattr(
        user_profile_service.user_profile_repository,
        "update_profile",
        lambda user_id, data: {
            **saved_profile,
            "weight_kg": 80
        }
    )

    result = user_profile_service.update_profile(
        1,
        UserProfileUpdate(weight_kg=80)
    )

    assert result["weight_kg"] == 80


def test_update_profile_not_found(monkeypatch):
    monkeypatch.setattr(
        user_profile_service.user_profile_repository,
        "update_profile",
        lambda user_id, data: None
    )

    with pytest.raises(HTTPException) as error:
        user_profile_service.update_profile(
            999,
            UserProfileUpdate(weight_kg=80)
        )

    assert error.value.status_code == 404


def test_delete_profile(monkeypatch):
    monkeypatch.setattr(
        user_profile_service.user_profile_repository,
        "delete_profile",
        lambda user_id: {"id": 10}
    )

    result = user_profile_service.delete_profile(1)

    assert result == {"id": 10}


def test_delete_profile_not_found(monkeypatch):
    monkeypatch.setattr(
        user_profile_service.user_profile_repository,
        "delete_profile",
        lambda user_id: None
    )

    with pytest.raises(HTTPException) as error:
        user_profile_service.delete_profile(999)

    assert error.value.status_code == 404
