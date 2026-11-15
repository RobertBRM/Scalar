
import pytest
from pydantic import ValidationError

from app.models.food import (
    FoodCreate,
    FoodUpdate,
    FoodResponse
)


def test_create_food_valid(valid_food):
    food = FoodCreate(**valid_food)

    assert food.name == "Eggs"
    assert food.calories == 155
    assert food.protein_g == 13


def test_create_food_missing_name(valid_food):
    del valid_food["name"]

    with pytest.raises(ValidationError):
        FoodCreate(**valid_food)


def test_create_food_empty_name(valid_food):
    valid_food["name"] = ""

    with pytest.raises(ValidationError):
        FoodCreate(**valid_food)


@pytest.mark.parametrize(
    "field,value",
    [
        ("calories", -1),
        ("protein_g", -1),
        ("carbs_g", -1),
        ("fat_g", -1),
        ("fiber_g", -1),
        ("serving_size", 0)
    ]
)
def test_create_food_invalid_values(
    valid_food, field, value
):
    valid_food[field] = value

    with pytest.raises(ValidationError):
        FoodCreate(**valid_food)


def test_create_food_rejects_extra_fields(valid_food):
    valid_food["unknown"] = "value"

    with pytest.raises(ValidationError):
        FoodCreate(**valid_food)


def test_update_food_partial():
    food = FoodUpdate(calories=200)

    assert food.model_dump(exclude_unset=True) == {
        "calories": 200
    }


def test_update_food_empty():
    food = FoodUpdate()

    assert food.model_dump(exclude_unset=True) == {}


def test_update_food_invalid_calories():
    with pytest.raises(ValidationError):
        FoodUpdate(calories=-10)


def test_food_response(saved_food):
    food = FoodResponse(**saved_food)

    assert food.id == 1
    assert food.name == "Eggs"

