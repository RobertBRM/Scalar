
from unittest.mock import MagicMock

import pytest

from app.repositories import user_repository


@pytest.fixture
def mock_db(monkeypatch):
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    monkeypatch.setattr(
        user_repository,
        "get_connection",
        lambda: connection
    )

    return cursor


def test_create_user(mock_db, valid_user, saved_user):
    mock_db.fetchone.return_value = saved_user

    result = user_repository.create_user(
        email=valid_user["email"],
        password_hash="demo-hash-not-a-real-password"
    )

    assert result["id"] == 1
    mock_db.execute.assert_called_once()


def test_get_user_by_id(mock_db, saved_user):
    mock_db.fetchone.return_value = saved_user

    result = user_repository.get_user_by_id(1)

    assert result["id"] == 1
    mock_db.execute.assert_called_once()


def test_get_user_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = user_repository.get_user_by_id(999)

    assert result is None


def test_update_user(mock_db, saved_user):
    mock_db.fetchone.return_value = {
        **saved_user,
        "email": "new@example.com"
    }

    result = user_repository.update_user(
        user_id=1,
        email="new@example.com",
        password_hash=None
    )

    assert result["email"] == "new@example.com"
    mock_db.execute.assert_called_once()


def test_update_user_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = user_repository.update_user(
        user_id=999,
        email="new@example.com",
        password_hash=None
    )

    assert result is None


def test_delete_user(mock_db):
    mock_db.fetchone.return_value = {"id": 1}

    result = user_repository.delete_user(1)

    assert result == {"id": 1}
    mock_db.execute.assert_called_once()


def test_delete_user_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = user_repository.delete_user(999)

    assert result is None
