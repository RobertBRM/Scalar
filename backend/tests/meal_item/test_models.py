
import pytest
from pydantic import ValidationError

from app.models.meal_item import (
    MealItemCreate,
    MealItemUpdate,
    MealItemResponse
)


def test_create_meal_item_valid(valid_meal_item):
    item = MealItemCreate(**valid_meal_item)

    assert item.meal_id == 10
    assert item.food_id == 5
    assert item.quantity == 2


@pytest.mark.parametrize(
    "field",
    ["meal_id", "food_id", "quantity"]
)
def test_create_meal_item_missing_field(
    valid_meal_item, field
):
    del valid_meal_item[field]

    with pytest.raises(ValidationError):
        MealItemCreate(**valid_meal_item)


@pytest.mark.parametrize(
    "field,value",
    [
        ("meal_id", 0),
        ("meal_id", -1),
        ("food_id", 0),
        ("food_id", -1),
        ("quantity", 0),
        ("quantity", -1)
    ]
)
def test_create_meal_item_invalid_values(
    valid_meal_item, field, value
):
    valid_meal_item[field] = value

    with pytest.raises(ValidationError):
        MealItemCreate(**valid_meal_item)


def test_create_meal_item_extra_field(valid_meal_item):
    valid_meal_item["unknown"] = "invalid"

    with pytest.raises(ValidationError):
        MealItemCreate(**valid_meal_item)


def test_update_meal_item_partial():
    item = MealItemUpdate(quantity=3)

    assert item.model_dump(exclude_unset=True) == {
        "quantity": 3
    }


def test_update_meal_item_empty():
    item = MealItemUpdate()

    assert item.model_dump(exclude_unset=True) == {}


def test_update_meal_item_invalid_quantity():
    with pytest.raises(ValidationError):
        MealItemUpdate(quantity=0)


def test_meal_item_response(saved_meal_item):
    item = MealItemResponse(**saved_meal_item)

    assert item.id == 20
    assert item.meal_id == 10
    assert item.food_id == 5
    assert item.quantity == 2
