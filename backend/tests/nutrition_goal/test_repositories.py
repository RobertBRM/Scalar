
from unittest.mock import MagicMock

import pytest

from app.models.nutrition_goal import (
    NutritionGoalCreate,
    NutritionGoalUpdate
)

from app.repositories import nutrition_goal_repository


@pytest.fixture
def mock_db(monkeypatch):
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    monkeypatch.setattr(
        nutrition_goal_repository,
        "get_connection",
        lambda: connection
    )

    return cursor


def test_create_goal(mock_db, valid_goal, saved_goal):
    mock_db.fetchone.return_value = saved_goal

    result = nutrition_goal_repository.create_nutrition_goal(
        NutritionGoalCreate(**valid_goal)
    )

    assert result == saved_goal
    mock_db.execute.assert_called_once()


def test_get_goal_by_user(mock_db, saved_goal):
    mock_db.fetchone.return_value = saved_goal

    result = (
        nutrition_goal_repository
        .get_nutrition_goal_by_user_id(1)
    )

    assert result["user_id"] == 1
    mock_db.execute.assert_called_once()


def test_get_goal_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = (
        nutrition_goal_repository
        .get_nutrition_goal_by_user_id(999)
    )

    assert result is None


def test_update_goal(mock_db, saved_goal):
    mock_db.fetchone.return_value = {
        **saved_goal,
        "calorie_goal": 2500
    }

    result = nutrition_goal_repository.update_nutrition_goal(
        1,
        NutritionGoalUpdate(calorie_goal=2500)
    )

    assert result["calorie_goal"] == 2500
    mock_db.execute.assert_called_once()


def test_update_goal_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = nutrition_goal_repository.update_nutrition_goal(
        999,
        NutritionGoalUpdate(calorie_goal=2500)
    )

    assert result is None


def test_delete_goal(mock_db):
    mock_db.fetchone.return_value = {"id": 10}

    result = nutrition_goal_repository.delete_nutrition_goal(
        1
    )

    assert result == {"id": 10}


def test_delete_goal_not_found(mock_db):
    mock_db.fetchone.return_value = None

    result = nutrition_goal_repository.delete_nutrition_goal(
        999
    )

    assert result is None

