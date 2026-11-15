
from unittest.mock import MagicMock

import pytest

from app.models.food import FoodCreate, FoodUpdate
from app.repositories import food_repository


@pytest.fixture
def mock_db(monkeypatch):
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    monkeypatch.setattr(
        food_repository,
        "get_connection",
        lambda: connection
    )

    return cursor


def test_create_food(mock_db, valid_food, saved_food):
    mock_db.fetchone.return_value = saved_food

    result = food_repository.create_food(
        FoodCreate(**valid_food)
    )

    assert result == saved_food
    mock_db.execute.assert_called_once()


def test_get_food_by_id(mock_db, saved_food):
    mock_db.fetchone.return_value = saved_food

    result = food_repository.get_food_by_id(1)

    assert result["id"] == 1
    mock_db.execute.assert_called_once()


def test_get_food_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = food_repository.get_food_by_id(999)

    assert result is None


def test_get_all_foods(mock_db, saved_food):
    mock_db.fetchall.return_value = [saved_food]

    result = food_repository.get_all_foods()

    assert len(result) == 1
    assert result[0]["name"] == "Eggs"


def test_search_foods(mock_db, saved_food):
    mock_db.fetchall.return_value = [saved_food]

    result = food_repository.search_foods("Egg")

    assert len(result) == 1
    assert mock_db.execute.call_args.args[1] == ("%Egg%",)


def test_update_food(mock_db, saved_food):
    mock_db.fetchone.return_value = {
        **saved_food,
        "calories": 200
    }

    result = food_repository.update_food(
        1,
        FoodUpdate(calories=200)
    )

    assert result["calories"] == 200
    mock_db.execute.assert_called_once()


def test_update_food_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = food_repository.update_food(
        999,
        FoodUpdate(calories=200)
    )

    assert result is None


def test_delete_food(mock_db):
    mock_db.fetchone.return_value = {"id": 1}

    result = food_repository.delete_food(1)

    assert result == {"id": 1}
    mock_db.execute.assert_called_once()


def test_delete_food_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = food_repository.delete_food(999)

    assert result is None

