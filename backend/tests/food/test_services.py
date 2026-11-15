
import pytest
from fastapi import HTTPException

from app.models.food import FoodCreate, FoodUpdate
from app.services import food_service


def test_create_food(monkeypatch, valid_food, saved_food):
    monkeypatch.setattr(
        food_service.food_repository,
        "create_food",
        lambda food: saved_food
    )

    result = food_service.create_food(
        FoodCreate(**valid_food)
    )

    assert result == saved_food


def test_get_food_success(monkeypatch, saved_food):
    monkeypatch.setattr(
        food_service.food_repository,
        "get_food_by_id",
        lambda food_id: saved_food
    )

    result = food_service.get_food(1)

    assert result["id"] == 1


def test_get_food_not_found(monkeypatch):
    monkeypatch.setattr(
        food_service.food_repository,
        "get_food_by_id",
        lambda food_id: None
    )

    with pytest.raises(HTTPException) as error:
        food_service.get_food(999)

    assert error.value.status_code == 404


def test_get_all_foods(monkeypatch, saved_food):
    monkeypatch.setattr(
        food_service.food_repository,
        "get_all_foods",
        lambda: [saved_food]
    )

    assert len(food_service.get_all_foods()) == 1


def test_search_foods_trims_whitespace(
    monkeypatch, saved_food
):
    received = []

    def fake_search(name):
        received.append(name)
        return [saved_food]

    monkeypatch.setattr(
        food_service.food_repository,
        "search_foods",
        fake_search
    )

    result = food_service.search_foods("  Egg  ")

    assert received == ["Egg"]
    assert len(result) == 1


def test_search_foods_empty():
    with pytest.raises(HTTPException) as error:
        food_service.search_foods("   ")

    assert error.value.status_code == 400


def test_update_food_success(monkeypatch, saved_food):
    monkeypatch.setattr(
        food_service.food_repository,
        "update_food",
        lambda food_id, data: {
            **saved_food,
            "calories": 200
        }
    )

    result = food_service.update_food(
        1,
        FoodUpdate(calories=200)
    )

    assert result["calories"] == 200


def test_update_food_not_found(monkeypatch):
    monkeypatch.setattr(
        food_service.food_repository,
        "update_food",
        lambda food_id, data: None
    )

    with pytest.raises(HTTPException) as error:
        food_service.update_food(
            999,
            FoodUpdate(calories=200)
        )

    assert error.value.status_code == 404


def test_delete_food_success(monkeypatch):
    monkeypatch.setattr(
        food_service.food_repository,
        "delete_food",
        lambda food_id: {"id": food_id}
    )

    assert food_service.delete_food(1) == {"id": 1}


def test_delete_food_not_found(monkeypatch):
    monkeypatch.setattr(
        food_service.food_repository,
        "delete_food",
        lambda food_id: None
    )

    with pytest.raises(HTTPException) as error:
        food_service.delete_food(999)

    assert error.value.status_code == 404

