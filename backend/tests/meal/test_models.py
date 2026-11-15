
import pytest
from pydantic import ValidationError

from app.models.meal import (
    MealCreate,
    MealUpdate,
    MealResponse
)


def test_create_meal_valid(valid_meal):
    meal = MealCreate(**valid_meal)

    assert meal.user_id == 1
    assert meal.meal_type == "breakfast"


def test_create_meal_missing_user(valid_meal):
    del valid_meal["user_id"]

    with pytest.raises(ValidationError):
        MealCreate(**valid_meal)


def test_create_meal_invalid_user(valid_meal):
    valid_meal["user_id"] = -1

    with pytest.raises(ValidationError):
        MealCreate(**valid_meal)


def test_create_meal_missing_type(valid_meal):
    del valid_meal["meal_type"]

    with pytest.raises(ValidationError):
        MealCreate(**valid_meal)


def test_create_meal_extra_field(valid_meal):
    valid_meal["unknown"] = "invalid"

    with pytest.raises(ValidationError):
        MealCreate(**valid_meal)


def test_update_meal_partial():
    meal = MealUpdate(meal_type="lunch")

    assert meal.model_dump(exclude_unset=True) == {
        "meal_type": "lunch"
    }


def test_update_meal_empty():
    meal = MealUpdate()

    assert meal.model_dump(exclude_unset=True) == {}


def test_meal_response(saved_meal):
    meal = MealResponse(**saved_meal)

    assert meal.id == 10
    assert meal.user_id == 1

