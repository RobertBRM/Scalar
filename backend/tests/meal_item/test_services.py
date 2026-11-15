
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.models.meal_item import (
    MealItemCreate,
    MealItemUpdate
)

from app.services import meal_item_service


def test_create_meal_item(
    monkeypatch,
    valid_meal_item,
    saved_meal_item,
    saved_meal,
    saved_food
):
    monkeypatch.setattr(
        meal_item_service.meal_repository,
        "get_meal_by_id",
        lambda meal_id: saved_meal
    )

    monkeypatch.setattr(
        meal_item_service.food_repository,
        "get_food_by_id",
        lambda food_id: saved_food
    )

    monkeypatch.setattr(
        meal_item_service.meal_item_repository,
        "create_meal_item",
        lambda item: saved_meal_item
    )

    result = meal_item_service.create_meal_item(
        MealItemCreate(**valid_meal_item)
    )

    assert result == saved_meal_item


def test_create_meal_not_found(
    monkeypatch, valid_meal_item
):
    monkeypatch.setattr(
        meal_item_service.meal_repository,
        "get_meal_by_id",
        lambda meal_id: None
    )

    with pytest.raises(HTTPException) as error:
        meal_item_service.create_meal_item(
            MealItemCreate(**valid_meal_item)
        )

    assert error.value.status_code == 404


def test_create_food_not_found(
    monkeypatch, valid_meal_item, saved_meal
):
    monkeypatch.setattr(
        meal_item_service.meal_repository,
        "get_meal_by_id",
        lambda meal_id: saved_meal
    )

    monkeypatch.setattr(
        meal_item_service.food_repository,
        "get_food_by_id",
        lambda food_id: None
    )

    with pytest.raises(HTTPException) as error:
        meal_item_service.create_meal_item(
            MealItemCreate(**valid_meal_item)
        )

    assert error.value.status_code == 404


def test_get_meal_item(
    monkeypatch, saved_meal_item
):
    monkeypatch.setattr(
        meal_item_service.meal_item_repository,
        "get_meal_item_by_id",
        lambda item_id: saved_meal_item
    )

    result = meal_item_service.get_meal_item(20)

    assert result["id"] == 20


def test_get_meal_item_not_found(monkeypatch):
    monkeypatch.setattr(
        meal_item_service.meal_item_repository,
        "get_meal_item_by_id",
        lambda item_id: None
    )

    with pytest.raises(HTTPException) as error:
        meal_item_service.get_meal_item(999)

    assert error.value.status_code == 404


def test_get_meal_items(
    monkeypatch, saved_meal, saved_meal_item
):
    monkeypatch.setattr(
        meal_item_service.meal_repository,
        "get_meal_by_id",
        lambda meal_id: saved_meal
    )

    monkeypatch.setattr(
        meal_item_service.meal_item_repository,
        "get_items_by_meal",
        lambda meal_id: [saved_meal_item]
    )

    result = meal_item_service.get_meal_items(10)

    assert len(result) == 1


def test_get_meal_items_missing_meal(monkeypatch):
    monkeypatch.setattr(
        meal_item_service.meal_repository,
        "get_meal_by_id",
        lambda meal_id: None
    )

    with pytest.raises(HTTPException) as error:
        meal_item_service.get_meal_items(999)

    assert error.value.status_code == 404


def test_update_meal_item(
    monkeypatch, saved_meal_item
):
    monkeypatch.setattr(
        meal_item_service.meal_item_repository,
        "update_meal_item",
        lambda item_id, data: {
            **saved_meal_item,
            "quantity": 3
        }
    )

    result = meal_item_service.update_meal_item(
        20,
        MealItemUpdate(quantity=3)
    )

    assert result["quantity"] == 3


def test_update_meal_item_not_found(monkeypatch):
    monkeypatch.setattr(
        meal_item_service.meal_item_repository,
        "update_meal_item",
        lambda item_id, data: None
    )

    with pytest.raises(HTTPException) as error:
        meal_item_service.update_meal_item(
            999,
            MealItemUpdate(quantity=3)
        )

    assert error.value.status_code == 404


def test_delete_meal_item(monkeypatch):
    monkeypatch.setattr(
        meal_item_service.meal_item_repository,
        "delete_meal_item",
        lambda item_id: {"id": item_id}
    )

    result = meal_item_service.delete_meal_item(20)

    assert result == {"id": 20}


def test_delete_meal_item_not_found(monkeypatch):
    monkeypatch.setattr(
        meal_item_service.meal_item_repository,
        "delete_meal_item",
        lambda item_id: None
    )

    with pytest.raises(HTTPException) as error:
        meal_item_service.delete_meal_item(999)

    assert error.value.status_code == 404


def test_calculate_meal_nutrition(
    monkeypatch, saved_meal, saved_food
):
    items = [
        {"food_id": 5, "quantity": 2},
        {"food_id": 6, "quantity": 1}
    ]

    second_food = {
        "id": 6,
        "calories": 80,
        "protein_g": 4,
        "carbs_g": 15,
        "fat_g": 2
    }

    monkeypatch.setattr(
        meal_item_service.meal_repository,
        "get_meal_by_id",
        lambda meal_id: saved_meal
    )

    monkeypatch.setattr(
        meal_item_service.meal_item_repository,
        "get_items_by_meal",
        lambda meal_id: items
    )

    foods = {5: saved_food, 6: second_food}

    monkeypatch.setattr(
        meal_item_service.food_repository,
        "get_food_by_id",
        lambda food_id: foods.get(food_id)
    )

    result = meal_item_service.calculate_meal_nutrition(
        10
    )

    assert result["calories"] == Decimal("360")
    assert result["protein_g"] == Decimal("28")
    assert result["carbs_g"] == Decimal("19")
    assert result["fat_g"] == Decimal("22")


def test_calculate_empty_meal(
    monkeypatch, saved_meal
):
    monkeypatch.setattr(
        meal_item_service.meal_repository,
        "get_meal_by_id",
        lambda meal_id: saved_meal
    )

    monkeypatch.setattr(
        meal_item_service.meal_item_repository,
        "get_items_by_meal",
        lambda meal_id: []
    )

    result = meal_item_service.calculate_meal_nutrition(
        10
    )

    assert result["calories"] == 0
    assert result["protein_g"] == 0
    assert result["carbs_g"] == 0
    assert result["fat_g"] == 0


def test_calculate_missing_food(
    monkeypatch, saved_meal
):
    monkeypatch.setattr(
        meal_item_service.meal_repository,
        "get_meal_by_id",
        lambda meal_id: saved_meal
    )

    monkeypatch.setattr(
        meal_item_service.meal_item_repository,
        "get_items_by_meal",
        lambda meal_id: [
            {"food_id": 999, "quantity": 1}
        ]
    )

    monkeypatch.setattr(
        meal_item_service.food_repository,
        "get_food_by_id",
        lambda food_id: None
    )

    with pytest.raises(HTTPException) as error:
        meal_item_service.calculate_meal_nutrition(
            10
        )

    assert error.value.status_code == 404
