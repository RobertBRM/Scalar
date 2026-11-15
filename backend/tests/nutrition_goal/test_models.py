
import pytest
from pydantic import ValidationError

from app.models.nutrition_goal import (
    NutritionGoalCreate,
    NutritionGoalUpdate,
    NutritionGoalResponse
)


def test_create_goal_valid(valid_goal):
    goal = NutritionGoalCreate(**valid_goal)

    assert goal.user_id == 1
    assert goal.calorie_goal == 2200
    assert goal.protein_goal_g == 150


def test_create_goal_missing_user(valid_goal):
    del valid_goal["user_id"]

    with pytest.raises(ValidationError):
        NutritionGoalCreate(**valid_goal)


@pytest.mark.parametrize("user_id", [0, -1])
def test_create_goal_invalid_user(valid_goal, user_id):
    valid_goal["user_id"] = user_id

    with pytest.raises(ValidationError):
        NutritionGoalCreate(**valid_goal)


@pytest.mark.parametrize(
    "field",
    [
        "calorie_goal",
        "protein_goal_g",
        "carb_goal_g",
        "fat_goal_g",
        "water_goal_ml"
    ]
)
def test_create_goal_negative_values(valid_goal, field):
    valid_goal[field] = -1

    with pytest.raises(ValidationError):
        NutritionGoalCreate(**valid_goal)


def test_create_goal_extra_field(valid_goal):
    valid_goal["unknown_field"] = "invalid"

    with pytest.raises(ValidationError):
        NutritionGoalCreate(**valid_goal)


def test_update_goal_partial():
    goal = NutritionGoalUpdate(calorie_goal=2500)

    assert goal.model_dump(exclude_unset=True) == {
        "calorie_goal": 2500
    }


def test_update_goal_multiple_fields():
    goal = NutritionGoalUpdate(
        calorie_goal=2500,
        protein_goal_g=180
    )

    result = goal.model_dump(exclude_unset=True)

    assert result["calorie_goal"] == 2500
    assert result["protein_goal_g"] == 180


def test_update_goal_empty():
    goal = NutritionGoalUpdate()

    assert goal.model_dump(exclude_unset=True) == {}


def test_update_goal_invalid():
    with pytest.raises(ValidationError):
        NutritionGoalUpdate(calorie_goal=-100)


def test_goal_response(saved_goal):
    goal = NutritionGoalResponse(**saved_goal)

    assert goal.id == 10
    assert goal.user_id == 1
    assert goal.water_goal_ml == 2500

