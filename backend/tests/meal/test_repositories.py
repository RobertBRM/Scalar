
from unittest.mock import MagicMock

import pytest

from app.models.meal import MealCreate, MealUpdate
from app.repositories import meal_repository


@pytest.fixture
def mock_db(monkeypatch):
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    monkeypatch.setattr(
        meal_repository,
        "get_connection",
        lambda: connection
    )

    return cursor


def test_create_meal(mock_db, valid_meal, saved_meal):
    mock_db.fetchone.return_value = saved_meal

    result = meal_repository.create_meal(
        MealCreate(**valid_meal)
    )

    assert result == saved_meal
    mock_db.execute.assert_called_once()


def test_get_meal_by_id(mock_db, saved_meal):
    mock_db.fetchone.return_value = saved_meal

    result = meal_repository.get_meal_by_id(10)

    assert result["id"] == 10
    mock_db.execute.assert_called_once()


def test_get_meal_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = meal_repository.get_meal_by_id(999)

    assert result is None


def test_get_meals_by_user(mock_db, saved_meal):
    mock_db.fetchall.return_value = [saved_meal]

    result = meal_repository.get_meals_by_user(1)

    assert len(result) == 1
    assert result[0]["user_id"] == 1


def test_get_meals_by_user_empty(mock_db):
    mock_db.fetchall.return_value = []

    result = meal_repository.get_meals_by_user(1)

    assert result == []


def test_update_meal(mock_db, saved_meal):
    mock_db.fetchone.return_value = {
        **saved_meal,
        "meal_type": "lunch"
    }

    result = meal_repository.update_meal(
        10,
        MealUpdate(meal_type="lunch")
    )

    assert result["meal_type"] == "lunch"
    mock_db.execute.assert_called_once()


def test_update_meal_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = meal_repository.update_meal(
        999,
        MealUpdate(meal_type="lunch")
    )

    assert result is None


def test_delete_meal(mock_db):
    mock_db.fetchone.return_value = {"id": 10}

    result = meal_repository.delete_meal(10)

    assert result == {"id": 10}


def test_delete_meal_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = meal_repository.delete_meal(999)

    assert result is None

