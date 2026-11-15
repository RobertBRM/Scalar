
import pytest
from fastapi import HTTPException

from app.models.meal import MealCreate, MealUpdate
from app.services import meal_service


def test_create_meal(
    monkeypatch, valid_meal, saved_meal
):
    monkeypatch.setattr(
        meal_service.user_repository,
        "get_user_by_id",
        lambda user_id: {"id": user_id}
    )

    monkeypatch.setattr(
        meal_service.meal_repository,
        "create_meal",
        lambda meal: saved_meal
    )

    result = meal_service.create_meal(
        MealCreate(**valid_meal)
    )

    assert result == saved_meal


def test_create_meal_user_not_found(
    monkeypatch, valid_meal
):
    monkeypatch.setattr(
        meal_service.user_repository,
        "get_user_by_id",
        lambda user_id: None
    )

    with pytest.raises(HTTPException) as error:
        meal_service.create_meal(
            MealCreate(**valid_meal)
        )

    assert error.value.status_code == 404


def test_get_meal(monkeypatch, saved_meal):
    monkeypatch.setattr(
        meal_service.meal_repository,
        "get_meal_by_id",
        lambda meal_id: saved_meal
    )

    result = meal_service.get_meal(10)

    assert result["id"] == 10


def test_get_meal_not_found(monkeypatch):
    monkeypatch.setattr(
        meal_service.meal_repository,
        "get_meal_by_id",
        lambda meal_id: None
    )

    with pytest.raises(HTTPException) as error:
        meal_service.get_meal(999)

    assert error.value.status_code == 404


def test_get_user_meals(monkeypatch, saved_meal):
    monkeypatch.setattr(
        meal_service.user_repository,
        "get_user_by_id",
        lambda user_id: {"id": user_id}
    )

    monkeypatch.setattr(
        meal_service.meal_repository,
        "get_meals_by_user",
        lambda user_id: [saved_meal]
    )

    result = meal_service.get_user_meals(1)

    assert len(result) == 1


def test_get_user_meals_user_not_found(monkeypatch):
    monkeypatch.setattr(
        meal_service.user_repository,
        "get_user_by_id",
        lambda user_id: None
    )

    with pytest.raises(HTTPException) as error:
        meal_service.get_user_meals(999)

    assert error.value.status_code == 404


def test_update_meal(monkeypatch, saved_meal):
    monkeypatch.setattr(
        meal_service.meal_repository,
        "update_meal",
        lambda meal_id, data: {
            **saved_meal,
            "meal_type": "lunch"
        }
    )

    result = meal_service.update_meal(
        10,
        MealUpdate(meal_type="lunch")
    )

    assert result["meal_type"] == "lunch"


def test_update_meal_not_found(monkeypatch):
    monkeypatch.setattr(
        meal_service.meal_repository,
        "update_meal",
        lambda meal_id, data: None
    )

    with pytest.raises(HTTPException) as error:
        meal_service.update_meal(
            999,
            MealUpdate(meal_type="lunch")
        )

    assert error.value.status_code == 404


def test_delete_meal(monkeypatch):
    monkeypatch.setattr(
        meal_service.meal_repository,
        "delete_meal",
        lambda meal_id: {"id": meal_id}
    )

    result = meal_service.delete_meal(10)

    assert result == {"id": 10}


def test_delete_meal_not_found(monkeypatch):
    monkeypatch.setattr(
        meal_service.meal_repository,
        "delete_meal",
        lambda meal_id: None
    )

    with pytest.raises(HTTPException) as error:
        meal_service.delete_meal(999)

    assert error.value.status_code == 404

