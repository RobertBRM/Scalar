
from fastapi import HTTPException, status
from decimal import Decimal

from app.repositories import (
    meal_repository,
    meal_item_repository,
    food_repository
)

from app.models.meal_item import (
    MealItemCreate,
    MealItemUpdate
)


def create_meal_item(item: MealItemCreate):
    meal = meal_repository.get_meal_by_id(
        item.meal_id
    )

    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )

    food = food_repository.get_food_by_id(
        item.food_id
    )

    if food is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )

    return meal_item_repository.create_meal_item(
        item
    )


def get_meal_item(item_id: int):
    item = meal_item_repository.get_meal_item_by_id(item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal item not found"
        )

    return item


def get_meal_items(meal_id: int):
    meal = meal_repository.get_meal_by_id(
        meal_id
    )

    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )

    return meal_item_repository.get_items_by_meal(
        meal_id
    )


def update_meal_item(
    item_id: int,
    data: MealItemUpdate
):
    updated_item = (
        meal_item_repository.update_meal_item(
            item_id, data
        )
    )

    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal item not found"
        )

    return updated_item


def delete_meal_item(item_id: int):
    deleted_item = (
        meal_item_repository.delete_meal_item(
            item_id
        )
    )

    if deleted_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal item not found"
        )

    return deleted_item

def calculate_meal_nutrition(meal_id: int):
    # Verify that the meal exists
    meal = meal_repository.get_meal_by_id(meal_id)

    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )

    # Retrieve all items belonging to this meal
    items = meal_item_repository.get_items_by_meal(meal_id)

    totals = {
        "calories": Decimal("0"),
        "protein_g": Decimal("0"),
        "carbs_g": Decimal("0"),
        "fat_g": Decimal("0")
    }

    for item in items:
        food = food_repository.get_food_by_id(
            item["food_id"]
        )

        if food is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food not found"
            )

        quantity = Decimal(str(item["quantity"]))

        for nutrient in totals:
            amount = Decimal(str(food[nutrient]))
            totals[nutrient] += amount * quantity

    return totals

