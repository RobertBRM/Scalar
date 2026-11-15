
from unittest.mock import MagicMock

import pytest

from app.models.meal_item import (
    MealItemCreate,
    MealItemUpdate
)

from app.repositories import meal_item_repository


@pytest.fixture
def mock_db(monkeypatch):
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    monkeypatch.setattr(
        meal_item_repository,
        "get_connection",
        lambda: connection
    )

    return cursor


def test_create_meal_item(
    mock_db, valid_meal_item, saved_meal_item
):
    mock_db.fetchone.return_value = saved_meal_item

    result = meal_item_repository.create_meal_item(
        MealItemCreate(**valid_meal_item)
    )

    assert result == saved_meal_item
    mock_db.execute.assert_called_once()


def test_get_meal_item_by_id(
    mock_db, saved_meal_item
):
    mock_db.fetchone.return_value = saved_meal_item

    result = meal_item_repository.get_meal_item_by_id(
        20
    )

    assert result["id"] == 20
    mock_db.execute.assert_called_once()


def test_get_meal_item_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = meal_item_repository.get_meal_item_by_id(
        999
    )

    assert result is None


def test_get_items_by_meal(
    mock_db, saved_meal_item
):
    mock_db.fetchall.return_value = [saved_meal_item]

    result = meal_item_repository.get_items_by_meal(
        10
    )

    assert len(result) == 1
    assert result[0]["meal_id"] == 10


def test_get_items_by_meal_empty(mock_db):
    mock_db.fetchall.return_value = []

    result = meal_item_repository.get_items_by_meal(
        10
    )

    assert result == []


def test_update_meal_item(
    mock_db, saved_meal_item
):
    mock_db.fetchone.return_value = {
        **saved_meal_item,
        "quantity": 3
    }

    result = meal_item_repository.update_meal_item(
        20,
        MealItemUpdate(quantity=3)
    )

    assert result["quantity"] == 3
    mock_db.execute.assert_called_once()


def test_update_meal_item_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = meal_item_repository.update_meal_item(
        999,
        MealItemUpdate(quantity=3)
    )

    assert result is None


def test_delete_meal_item(mock_db):
    mock_db.fetchone.return_value = {"id": 20}

    result = meal_item_repository.delete_meal_item(
        20
    )

    assert result == {"id": 20}


def test_delete_meal_item_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = meal_item_repository.delete_meal_item(
        999
    )

    assert result is None
