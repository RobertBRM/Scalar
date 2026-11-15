
import pytest
from fastapi import HTTPException

from app.models.nutrition_goal import (
    NutritionGoalCreate,
    NutritionGoalUpdate
)
from app.services import nutrition_goal_service


def test_create_goal(
    monkeypatch, valid_goal, saved_goal
):
    monkeypatch.setattr(
        nutrition_goal_service.user_repository,
        "get_user_by_id",
        lambda user_id: {"id": user_id}
    )

    monkeypatch.setattr(
        nutrition_goal_service.nutrition_goal_repository,
        "get_nutrition_goal_by_user_id",
        lambda user_id: None
    )

    monkeypatch.setattr(
        nutrition_goal_service.nutrition_goal_repository,
        "create_nutrition_goal",
        lambda goal: saved_goal
    )

    result = nutrition_goal_service.create_nutrition_goal(
        NutritionGoalCreate(**valid_goal)
    )

    assert result["id"] == 10


def test_create_goal_user_not_found(
    monkeypatch, valid_goal
):
    monkeypatch.setattr(
        nutrition_goal_service.user_repository,
        "get_user_by_id",
        lambda user_id: None
    )

    with pytest.raises(HTTPException) as error:
        nutrition_goal_service.create_nutrition_goal(
            NutritionGoalCreate(**valid_goal)
        )

    assert error.value.status_code == 404


def test_create_duplicate_goal(
    monkeypatch, valid_goal, saved_goal
):
    monkeypatch.setattr(
        nutrition_goal_service.user_repository,
        "get_user_by_id",
        lambda user_id: {"id": user_id}
    )

    monkeypatch.setattr(
        nutrition_goal_service.nutrition_goal_repository,
        "get_nutrition_goal_by_user_id",
        lambda user_id: saved_goal
    )

    with pytest.raises(HTTPException) as error:
        nutrition_goal_service.create_nutrition_goal(
            NutritionGoalCreate(**valid_goal)
        )

    assert error.value.status_code == 409


def test_get_goal(monkeypatch, saved_goal):
    monkeypatch.setattr(
        nutrition_goal_service.nutrition_goal_repository,
        "get_nutrition_goal_by_user_id",
        lambda user_id: saved_goal
    )

    result = nutrition_goal_service.get_nutrition_goal(1)

    assert result["calorie_goal"] == 2200


def test_get_goal_not_found(monkeypatch):
    monkeypatch.setattr(
        nutrition_goal_service.nutrition_goal_repository,
        "get_nutrition_goal_by_user_id",
        lambda user_id: None
    )

    with pytest.raises(HTTPException) as error:
        nutrition_goal_service.get_nutrition_goal(999)

    assert error.value.status_code == 404


def test_update_goal(monkeypatch, saved_goal):
    monkeypatch.setattr(
        nutrition_goal_service.nutrition_goal_repository,
        "update_nutrition_goal",
        lambda user_id, data: {
            **saved_goal,
            "calorie_goal": 2500
        }
    )

    result = nutrition_goal_service.update_nutrition_goal(
        1,
        NutritionGoalUpdate(calorie_goal=2500)
    )

    assert result["calorie_goal"] == 2500


def test_update_goal_not_found(monkeypatch):
    monkeypatch.setattr(
        nutrition_goal_service.nutrition_goal_repository,
        "update_nutrition_goal",
        lambda user_id, data: None
    )

    with pytest.raises(HTTPException) as error:
        nutrition_goal_service.update_nutrition_goal(
            999,
            NutritionGoalUpdate(calorie_goal=2500)
        )

    assert error.value.status_code == 404


def test_delete_goal(monkeypatch):
    monkeypatch.setattr(
        nutrition_goal_service.nutrition_goal_repository,
        "delete_nutrition_goal",
        lambda user_id: {"id": 10}
    )

    result = nutrition_goal_service.delete_nutrition_goal(1)

    assert result == {"id": 10}


def test_delete_goal_not_found(monkeypatch):
    monkeypatch.setattr(
        nutrition_goal_service.nutrition_goal_repository,
        "delete_nutrition_goal",
        lambda user_id: None
    )

    with pytest.raises(HTTPException) as error:
        nutrition_goal_service.delete_nutrition_goal(999)

    assert error.value.status_code == 404

