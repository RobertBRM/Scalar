
from unittest.mock import MagicMock

import pytest

from app.models.user_profile import (
    UserProfileCreate,
    UserProfileUpdate
)

from app.repositories import user_profile_repository


@pytest.fixture
def mock_db(monkeypatch):
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    monkeypatch.setattr(
        user_profile_repository,
        "get_connection",
        lambda: connection
    )

    return cursor


def test_create_profile(
    mock_db, valid_profile, saved_profile
):
    mock_db.fetchone.return_value = saved_profile

    result = user_profile_repository.create_user_profile(
        UserProfileCreate(**valid_profile)
    )

    assert result == saved_profile
    mock_db.execute.assert_called_once()


def test_get_profile_by_user(
    mock_db, saved_profile
):
    mock_db.fetchone.return_value = saved_profile

    result = (
        user_profile_repository
        .get_user_profile_by_user_id(1)
    )

    assert result["user_id"] == 1
    mock_db.execute.assert_called_once()


def test_get_profile_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = (
        user_profile_repository
        .get_user_profile_by_user_id(999)
    )

    assert result is None


def test_update_profile(mock_db, saved_profile):
    mock_db.fetchone.return_value = {
        **saved_profile,
        "weight_kg": 80
    }

    result = user_profile_repository.update_user_profile(
        1,
        UserProfileUpdate(weight_kg=80)
    )

    assert result["weight_kg"] == 80
    mock_db.execute.assert_called_once()


def test_update_profile_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = user_profile_repository.update_user_profile(
        999,
        UserProfileUpdate(weight_kg=80)
    )

    assert result is None


def test_delete_profile(mock_db):
    mock_db.fetchone.return_value = {"id": 10}

    result = user_profile_repository.delete_user_profile(
        1
    )

    assert result == {"id": 10}


def test_delete_profile_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = user_profile_repository.delete_user_profile(
        999
    )

    assert result is None

